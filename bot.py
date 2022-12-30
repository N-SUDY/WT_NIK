import os
import time
import json
import random
import asyncio
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
from core.ffmpeg import vidmark
from core.clean import delete_all, delete_trash
from pyrogram import Client, filters
from configs import Config
from core.handlers.main_db_handler import db
from core.display_progress import progress_for_pyrogram, humanbytes
from core.handlers.upload_video_handler import send_video_handler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors.exceptions.flood_420 import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified



USER = Client(
			name = "WatermarkBOT",
			session_string = Config.Session_String,
			api_id = Config.API_ID,
			api_hash = Config.API_HASH
		)
USER.start()
x = USER.get_me()
uid = x.id

AHBot = Client("WT", bot_token=Config.BOT_TOKEN, api_id=Config.API_ID, api_hash=Config.API_HASH)






async def _check_user(filt, c, m):
    chat_id = m.chat.id
    if chat_id==Config.GROUP_ID and m.from_user.id!=uid:
        return True
    else :
        return False

check_user = filters.create(_check_user)



@AHBot.on_message(filters.command(["start", "help"]) & check_user)
async def HelpWatermark(_, cmd):
        if not await db.is_user_exist(cmd.from_user.id):
            await db.add_user(cmd.from_user.id)
        await cmd.reply_text(
				text="Hi, I am Video Watermark Adder Bot!\n**How to Added Watermark to a Video?**\n**Usage:** First Send a JPG Image/Logo, then send any Video. Better add watermark to a MP4 or MKV Video.\nNote: I can only process one video at a time. As my server is Heroku, my health is not good. If you have any issues with Adding Watermark to a Video",disable_web_page_preview=True
			)


@AHBot.on_message(filters.command(["reset"])  & check_user)
async def reset(_, update):
        await db.delete_user(update.from_user.id)
        await db.add_user(update.from_user.id)
        await update.reply_text("Settings reseted successfully")


@AHBot.on_message(filters.command("settings")  & check_user)
async def SettingsBot(_, cmd):
				if not await db.is_user_exist(cmd.from_user.id):
					await db.add_user(cmd.from_user.id)

				## --- Checks --- ##
				position_tag = None
				watermark_position = await db.get_position(cmd.from_user.id)
				if watermark_position == "5:main_h-overlay_h":
					position_tag = "Bottom Left"
				elif watermark_position == "main_w-overlay_w-5:main_h-overlay_h-5":
					position_tag = "Bottom Right"
				elif watermark_position == "main_w-overlay_w-5:5":
					position_tag = "Top Right"
				elif watermark_position == "5:5":
					position_tag = "Top Left"

				watermark_size = await db.get_size(cmd.from_user.id)
				if int(watermark_size) == 5:
					size_tag = "5%"
				elif int(watermark_size) == 7:
					size_tag = "7%"
				elif int(watermark_size) == 10:
					size_tag = "10%"
				elif int(watermark_size) == 15:
					size_tag = "15%"
				elif int(watermark_size) == 20:
					size_tag = "20%"
				elif int(watermark_size) == 25:
					size_tag = "25%"
				elif int(watermark_size) == 30:
					size_tag = "30%"
				elif int(watermark_size) == 35:
					size_tag = "35%"
				elif int(watermark_size) == 40:
					size_tag = "40%"
				elif int(watermark_size) == 45:
					size_tag = "45%"
				else:
					size_tag = "7%"
				## --- Next --- ##
				BUTTONS =[
							[InlineKeyboardButton(f"Watermark Position - {position_tag}", callback_data="lol")],
							[InlineKeyboardButton("Set Top Left", callback_data=f"position_5:5"), InlineKeyboardButton("Set Top Right", callback_data=f"position_main_w-overlay_w-5:5")],
							[InlineKeyboardButton("Set Bottom Left", callback_data=f"position_5:main_h-overlay_h"), InlineKeyboardButton("Set Bottom Right", callback_data=f"position_main_w-overlay_w-5:main_h-overlay_h-5")],
							[InlineKeyboardButton(f"Watermark Size - {size_tag}", callback_data="lel")],
							[InlineKeyboardButton("5%", callback_data=f"size_5"), InlineKeyboardButton("7%", callback_data=f"size_7"), InlineKeyboardButton("10%", callback_data=f"size_10"), InlineKeyboardButton("15%", callback_data=f"size_15"), InlineKeyboardButton("20%", callback_data=f"size_20")],
							[InlineKeyboardButton("25%", callback_data=f"size_25"), InlineKeyboardButton("30%", callback_data=f"size_30"), InlineKeyboardButton("35%", callback_data=f"size_30"), InlineKeyboardButton("40%", callback_data=f"size_40"), InlineKeyboardButton("45%", callback_data=f"size_45")],
							[InlineKeyboardButton(f"Reset Settings To Default", callback_data="reset")]
						]
				print(BUTTONS)
				await cmd.reply_text(
					text="Here you can set your Watermark Settings:",
					disable_web_page_preview=True,
					reply_markup= InlineKeyboardMarkup(BUTTONS)
					)



@AHBot.on_message((filters.document | filters.video | filters.photo)  & check_user)
async def VidWatermarkAdder(bot, cmd):
	if not await db.is_user_exist(cmd.from_user.id):
		await db.add_user(cmd.from_user.id)
	## --- Noobie Process --- ##
	if cmd.photo or (cmd.document and cmd.document.mime_type.startswith("image/")):
		editable = await cmd.reply_text("🔽Downloading Your Image.")
		watermark_path = Config.DOWN_PATH + "/" + str(cmd.from_user.id) + "/thumb.jpg"
		await asyncio.sleep(5)
		c_time = time.time()
		await bot.download_media(
			message=cmd,
			file_name=watermark_path,
		)
		await editable.delete()
		await cmd.reply_text("🔶This Saved as Next Video Watermark!\n\nNow Send any Video to start adding Watermark to that Video!")
		return
	else:
		pass
	working_dir = Config.DOWN_PATH + "/WatermarkAdder/"
	if not os.path.exists(working_dir):
		os.makedirs(working_dir)
	watermark_path = Config.DOWN_PATH + "/" + str(cmd.from_user.id) + "/thumb.jpg"
	if not os.path.exists(watermark_path):
		await cmd.reply_text("❌You Didn't Set Any Watermark!\n\nSave Watermark image first.")
		return
	file_type = cmd.video or cmd.document
	if not file_type.mime_type.startswith("video/"):
		await cmd.reply_text("❌This is not a Video!")
		return
	status = Config.DOWN_PATH + "/WatermarkAdder/status.json"
	if os.path.exists(status):
		await cmd.reply_text("Sorry, Currently I am busy with another Task!\n\nTry Again After Sometime!")
		return
	preset = Config.PRESET
	editable = await cmd.reply_text("🔽Downloading Video.")
	with open(status, "w") as f:
		statusMsg = {
			'chat_id': cmd.from_user.id,
			'message': editable.id
		}
		json.dump(statusMsg, f, indent=2)
	dl_loc = Config.DOWN_PATH + "/WatermarkAdder/" + str(cmd.from_user.id) + "/"
	if not os.path.isdir(dl_loc):
		os.makedirs(dl_loc)
	the_media = None
	try:
		c_time = time.time()
		m = await USER.get_messages(cmd.chat.id, cmd.id, replies=0)
		the_media = await USER.download_media(
			message=m,
			file_name=dl_loc,
			progress=progress_for_pyrogram,
			progress_args=(
				"🔽Downloading Video.",
				editable,
				c_time
			)
		)
		if the_media is None:
			await delete_trash(status)
			await delete_trash(the_media)
			print(f"❌Download Failed")
			await editable.edit("❗Unable to Download The Video!")
			return
	except Exception as err:
		await delete_trash(status)
		await delete_trash(the_media)
		print(f"❌Download Failed: {err}")
		await editable.edit("❗Unable to Download The Video!")
		return
	watermark_position = await db.get_position(cmd.from_user.id)
	if watermark_position == "5:main_h-overlay_h":
		position_tag = "Bottom Left"
	elif watermark_position == "main_w-overlay_w-5:main_h-overlay_h-5":
		position_tag = "Bottom Right"
	elif watermark_position == "main_w-overlay_w-5:5":
		position_tag = "Top Right"
	elif watermark_position == "5:5":
		position_tag = "Top Left"
	else:
		position_tag = "Top Left"
		watermark_position = "5:5"

	watermark_size = await db.get_size(cmd.from_user.id)
	await editable.edit(f"⌛Trying to Add Watermark to the Video at {position_tag} Corner.")
	duration = 0
	metadata = extractMetadata(createParser(the_media))
	if metadata.has("duration"):
		duration = metadata.get('duration').seconds
	the_media_file_name = os.path.basename(the_media)
	main_file_name = os.path.splitext(the_media_file_name)[0]
	output_vid = main_file_name + "_[" + str(cmd.from_user.id) + "]_[" + str(time.time()) + ".mp4"
	progress = Config.DOWN_PATH + "/WatermarkAdder/" + str(cmd.from_user.id) + "/progress.txt"
	try:
		output_vid = await vidmark(the_media, editable, progress, watermark_path, output_vid, duration, status, preset, watermark_position, watermark_size)
	except Exception as err:
		print(f"❌Unable to Add Watermark: {err}")
		await editable.edit("❗Unable to add Watermark!")
		await delete_all()
		return
	if output_vid is None:
		await editable.edit("❗Something went wrong!")
		await delete_all()
		return
	await editable.edit("✅Watermark Added Successfully!\n\n🔼Trying to Upload ...")
	width = 100
	height = 100
	duration = 0
	metadata = extractMetadata(createParser(output_vid))
	if metadata.has("duration"):
		duration = metadata.get('duration').seconds
	if metadata.has("width"):
		width = metadata.get("width")
	if metadata.has("height"):
		height = metadata.get("height")
	video_thumbnail = None
	try:
		video_thumbnail = Config.DOWN_PATH + "/WatermarkAdder/" + str(cmd.from_user.id) + "/" + str(time.time()) + ".jpg"
		ttl = random.randint(0, int(duration) - 1)
		file_genertor_command = [
			"ffmpeg",
			"-ss",
			str(ttl),
			"-i",
			output_vid,
			"-vframes",
			"1",
			video_thumbnail
		]
		process = await asyncio.create_subprocess_exec(
			*file_genertor_command,
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.PIPE,
		)
		stdout, stderr = await process.communicate()
		e_response = stderr.decode().strip()
		t_response = stdout.decode().strip()
		print(e_response)
		print(t_response)
		Image.open(video_thumbnail).convert("RGB").save(video_thumbnail)
		img = Image.open(video_thumbnail)
		img.resize((width, height))
		img.save(video_thumbnail, "JPEG")
	except Exception as err:
		print(f"Error: {err}")
	# --- Upload --- #
	file_size = os.path.getsize(output_vid)
	if (int(file_size) > 4294967296 ):
		await editable.edit(f"❗File Size Become {humanbytes(file_size)} !!\nI can't Upload to Telegram!")
		await delete_all()
		return
	try:
		await send_video_handler(USER, cmd, output_vid, video_thumbnail, duration, width, height, editable, file_size)
	except FloodWait as e:
		print(f"Got FloodWait of {e.x}s ...")
		await asyncio.sleep(e.x)
		await asyncio.sleep(5)
		await send_video_handler(USER, cmd, output_vid, video_thumbnail, duration, width, height, editable, file_size)
	except Exception as err:
		print(f"Unable to Upload Video: {err}")
		await editable.edit(f"❗ERROR: Unable to Upload Video!\n\n**Error:** `{err}`")
		await delete_all()
		return
	await delete_all()
	await editable.delete()
	return


@AHBot.on_message(filters.command("cancel")  & check_user)
async def CancelWatermarkAdder(bot, cmd):
	if not await db.is_user_exist(cmd.from_user.id):
		await db.add_user(cmd.from_user.id)
	if not int(cmd.from_user.id) == Config.OWNER_ID:
		await cmd.reply_text("You Can't Use That Command!")
		return

	status = Config.DOWN_PATH + "/WatermarkAdder/status.json"
	with open(status, 'r+') as f:
		statusMsg = json.load(f)
		if 'pid' in statusMsg.keys():
			try:
				os.kill(statusMsg["pid"], 9)
				await delete_trash(status)
			except Exception as err:
				print(err)
		await delete_all()
		await cmd.reply_text("Watermark Adding Process Stopped!")
		try:
			await bot.edit_message_text(chat_id=int(statusMsg["chat_id"]), message_id=int(statusMsg["message"]), text="🚦🚦 Last Process Stopped 🚦🚦")
		except:
			pass


@AHBot.on_message(filters.command("status") & check_user)
async def sts(_, m):
	status = Config.DOWN_PATH + "/WatermarkAdder/status.json"
	if os.path.exists(status):
		msg_text = "Sorry, Currently I am busy with another Task!\nI can't add Watermark at this moment."
	else:
		msg_text = "I am Free Now!\nSend me any video to add Watermark."
	if int(m.from_user.id) == Config.OWNER_ID:
		total_users = await db.total_users_count()
		msg_text += f"\n\n**Total Users in DB:** `{total_users}`"
	await m.reply_text(text=msg_text, quote=True)


@AHBot.on_callback_query()
async def button(bot, cmd: CallbackQuery):
	cb_data = cmd.data
	if "refreshmeh" in cb_data:
		await cmd.message.edit(
			text="Hi, I am Video Watermark Adder Bot!\n**How to Added Watermark to a Video?**\n**Usage:** First Send a JPG Image/Logo, then send any Video. Better add watermark to a MP4 or MKV Video.\nNote: I can only process one video at a time. As my server is Heroku, my health is not good. If you have any issues with Adding Watermark to a Video",
			reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Developer", url="https://t.me/AbirHasan2005"), InlineKeyboardButton("Support Group", url="https://t.me/DevsZone")], [InlineKeyboardButton("Bots Channel", url="https://t.me/Discovery_Updates")]]),
			disable_web_page_preview=True
		)

	elif "lol" in cb_data:
		await cmd.answer("Sir, that button not works XD\n\nPress Bottom Buttons to Set Position of Watermark!", show_alert=True)

	elif "lel" in cb_data:
		await cmd.answer("Sir, that button not works XD\n\nPress Bottom Buttons to Set Size of Watermark", show_alert=True)

	elif cb_data.startswith("position_") or cb_data.startswith("size_"):
		new_position = cb_data.split("_", 1)[1]
		if cb_data.startswith("position_"):
			await db.set_position(cmd.from_user.id, new_position)
		elif cb_data.startswith("size_"):
			await db.set_size(cmd.from_user.id, new_position)
		watermark_position = await db.get_position(cmd.from_user.id)
		if watermark_position == "5:main_h-overlay_h":
			position_tag = "Bottom Left"
		elif watermark_position == "main_w-overlay_w-5:main_h-overlay_h-5":
			position_tag = "Bottom Right"
		elif watermark_position == "main_w-overlay_w-5:5":
			position_tag = "Top Right"
		elif watermark_position == "5:5":
			position_tag = "Top Left"
		else:
			position_tag = "Top Left"

		watermark_size = await db.get_size(cmd.from_user.id)
		if int(watermark_size) == 5:
			size_tag = "5%"
		elif int(watermark_size) == 7:
			size_tag = "7%"
		elif int(watermark_size) == 10:
			size_tag = "10%"
		elif int(watermark_size) == 15:
			size_tag = "15%"
		elif int(watermark_size) == 20:
			size_tag = "20%"
		elif int(watermark_size) == 25:
			size_tag = "25%"
		elif int(watermark_size) == 30:
			size_tag = "30%"
		elif int(watermark_size) == 35:
			size_tag = "35%"
		elif int(watermark_size) == 40:
			size_tag = "40%"
		elif int(watermark_size) == 45:
			size_tag = "45%"
		else:
			size_tag = "7%"
		try:
			await cmd.message.edit(
				text="Here you can set your Watermark Settings:",
				disable_web_page_preview=True,
				reply_markup=InlineKeyboardMarkup(
					[
						[InlineKeyboardButton(f"Watermark Position - {position_tag}", callback_data="lol")],
						[InlineKeyboardButton("Set Top Left", callback_data=f"position_5:5"), InlineKeyboardButton("Set Top Right", callback_data=f"position_main_w-overlay_w-5:5")],
						[InlineKeyboardButton("Set Bottom Left", callback_data=f"position_5:main_h-overlay_h"), InlineKeyboardButton("Set Bottom Right", callback_data=f"position_main_w-overlay_w-5:main_h-overlay_h-5")],
						[InlineKeyboardButton(f"Watermark Size - {size_tag}", callback_data="lel")],
						[InlineKeyboardButton("5%", callback_data=f"size_5"), InlineKeyboardButton("7%", callback_data=f"size_7"), InlineKeyboardButton("10%", callback_data=f"size_10"), InlineKeyboardButton("15%", callback_data=f"size_15"), InlineKeyboardButton("20%", callback_data=f"size_20")],
						[InlineKeyboardButton("25%", callback_data=f"size_25"), InlineKeyboardButton("30%", callback_data=f"size_30"), InlineKeyboardButton("35%", callback_data=f"size_30"), InlineKeyboardButton("40%", callback_data=f"size_40"), InlineKeyboardButton("45%", callback_data=f"size_45")],
				                [InlineKeyboardButton(f"Reset Settings To Default", callback_data="reset")]
					]
				)
			)
		except MessageNotModified:
			pass

	elif "reset" in cb_data:
		await db.delete_user(cmd.from_user.id)
		await db.add_user(cmd.from_user.id)
		await cmd.answer("Settings Reseted Successfully!", show_alert=True)


print(f"⚡Bot By Sahil Nolia⚡")
AHBot.run()
