import flet as ft
import requests
import json
import urllib.request
from PIL import Image
import pyperclip

emojicolors = (
    (221, 46, 68, "🟥"),
    (244, 144, 12, "🟧"),
    (253, 203, 88, "🟨"),
    (120, 177, 89, "🟩",),
    (85, 172, 238, "🟦"),
    (170, 142, 214, "🟪"),
    (49, 55, 61, "⬛"),
    (230, 231, 232, "⬜"),
    (193, 105, 79, "🟫")
)


def nearest_colour(subjects, query):
    return min(subjects, key=lambda subject: sum((s - q) ** 2 for s, q in zip(subject, query)))


def generateplayeremoji(username, includelayer2):
    result = ""
    uuid_req = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
    uuid = json.loads(uuid_req.text).get("id")
    if uuid is None:
        return None
    else:
        urllib.request.urlretrieve(f"https://crafatar.com/skins/{uuid}", "./skin.png")

        skin = Image.open("./skin.png")
        skin_crop = skin.crop((8, 8, 16, 16))
        if includelayer2:
            skin_layer2 = skin.crop((40, 8, 48, 16))
            skin_crop.paste(skin_layer2, mask=skin_layer2)

        for y in range(8):
            for x in range(8):
                skin_crop = skin_crop.convert('RGB')
                pixelcolor = skin_crop.getpixel((x, y))
                closestemoji = nearest_colour(emojicolors, pixelcolor)
                result += closestemoji[3]
            result += "\n"
        return result


def main(page: ft.Page):
    page.title = "Emojify Minecraft skin"
    page.fonts = {
        "Twemoji": "https://artefacts.whynothugo.nl/twemoji.ttf/2024-06-06_17-55/Twemoji-15.1.0.ttf"
    }

    def startbuttonclicked(e):
        if playername.value == "":
            playername.error_text = "Enter your username"
            page.update()
        else:
            global result
            result = generateplayeremoji(playername.value, includelayer2switch.value)
            if result is None:
                playername.error_text = "This user does not exist"
            else:
                # resulttext.value = result
                resultdialog.content = ft.Row(controls=[ft.Text(result, font_family="Twemoji", )],
                                              alignment=ft.MainAxisAlignment.CENTER)
                page.open(resultdialog)
            page.update()

    def copyresult(e):
        pyperclip.copy(result)
        resultdialog.actions[0].icon = "check"
        page.update()

    def clearerrortext(e):
        playername.error_text = ""
        page.update()

    resultdialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Result"),
        # actions_alignment=ft.MainAxisAlignment.CENTER,
        actions=[
            ft.FilledButton("Copy", icon="CONTENT_COPY", on_click=copyresult, style=ft.ButtonStyle(
                padding=ft.padding.all(15)
            ), ),
            ft.FilledButton("Close", icon="CLOSE", on_click=lambda e: page.close(resultdialog), style=ft.ButtonStyle(
                padding=ft.padding.all(15)
            ))
        ]
    )
    title = ft.Container(content=ft.Text("Emojify Minecraft skin", theme_style=ft.TextThemeStyle.HEADLINE_LARGE),
                         margin=15)
    warningcontainer = ft.Container(
        content=ft.Row(spacing=15,
                       controls=[ft.Icon(name=ft.icons.WARNING), ft.Column(spacing=5, controls=[
                           ft.Text("Warning", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                           ft.Text("Result may not be good depends on your skins")])]),

        border_radius=10,
        margin=10,
        padding=10,
        bgcolor=ft.colors.PRIMARY_CONTAINER
    )
    playername = ft.TextField(label="Username", helper_text="Your Minecraft username, Java edition only",
                              on_change=clearerrortext)
    includelayer2switch = ft.Switch()
    playernamecont = ft.Container(margin=10,
                                  content=ft.Row(spacing=15, controls=[ft.Icon(name=ft.icons.SHORT_TEXT), playername]))
    includelayer2switchcont = ft.Container(
        margin=10,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=15,
                    controls=[
                        ft.Icon(name=ft.icons.LAYERS),
                        ft.Column(spacing=0,
                                  controls=[
                                      ft.Text("Include hat", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                                      ft.Text("Include layer 2")
                                  ]
                                  )
                    ]
                ),
                includelayer2switch
            ]
        )
    )
    resulttext = ft.Text(selectable=True)
    startbutton = ft.FloatingActionButton(icon=ft.icons.EMOJI_EMOTIONS, on_click=startbuttonclicked, text="Emojify")
    page.floating_action_button = startbutton
    page.add(title, warningcontainer, playernamecont, includelayer2switchcont, resulttext, )


ft.app(main)
