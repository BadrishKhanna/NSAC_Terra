
# video_globe_app.py
import sys
import os
import json
import requests
import re
from io import BytesIO
from PIL import Image
import cv2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QComboBox, QOpenGLWidget
)
from PyQt5.QtGui import QPixmap, QTextCursor, QTextCharFormat, QColor
from PyQt5.QtCore import Qt, QTimer
from OpenGL.GL import *
from OpenGL.GLU import *

# ----------------------------
# Helper: download files
# ----------------------------
def download_file(url, local_path, timeout=30):
    """Download url to local_path using requests. Return True on success."""
    try:
        r = requests.get(url, stream=True, timeout=timeout)
        r.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print("Download error:", e, url)
        return False

def download_image_to_pixmap(url):
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        pix = QPixmap()
        pix.loadFromData(r.content)
        return pix
    except Exception as e:
        print("Image download failed:", e, url)
        return None

def drive_to_direct(url):
    """
    Convert common Google Drive URL forms to a direct-uc download URL.
    If it's already a direct 'uc?id=...' or other direct link, return as-is.
    """
    if not url:
        return url
    # If already contains 'uc?id=' or 'export=download', leave it
    if "uc?export=download" in url or "uc?id=" in url:
        return url
    m = re.search(r"id=([A-Za-z0-9_\-]+)", url)
    if m:
        return f"https://drive.google.com/uc?id={m.group(1)}"
    # common alternate format: /file/d/<id>/...
    m2 = re.search(r"/d/([A-Za-z0-9_\-]+)", url)
    if m2:
        return f"https://drive.google.com/uc?id={m2.group(1)}"
    return url

# ----------------------------
# Built-in data: 10 forest-fire events
# (Populated from links you provided earlier.)
# ----------------------------
disasters = {
    "Forest Fire": [
        {
            "name": "Amazon Rainforest Fire",
            "location": "Brazil – 2019",
            "video": drive_to_direct("https://drive.google.com/uc?id=1bTx19oxt3T_X5qd4rFLIlH3KEkm7oeMk"),
            "text": drive_to_direct("https://drive.google.com/uc?id=1jV5tKOmAnIMVI0bu-qxT6Vo-N8CGinTg"),
            "right_images": [
                drive_to_direct("https://drive.google.com/uc?id=12SSqzs5yTR178dkJ9gI0FmmoGIgU6NRc"),
                drive_to_direct("https://drive.google.com/uc?id=1CkHf-dVF3SYV_b65s_gyScQMTEjHAOL3"),
                drive_to_direct("https://drive.google.com/uc?id=16O8CQ8ypPaulSBjSVepAlNtdMGu9NKrp"),
                drive_to_direct("https://drive.google.com/uc?id=15H3Op3lseMUyRQeUsKp2GMPFaKcDcv8v")
            ],
            "slideshow": [
                drive_to_direct("https://drive.google.com/uc?id=1ah-P4EtKR0noe1ypKGcm4-07_3Z13eQk"),
                drive_to_direct("https://drive.google.com/uc?id=10633_4iFloMdG8MsqBGZ54LV5PKixZCp"),
                drive_to_direct("https://drive.google.com/uc?id=13AkuKN1ueW0MjXdx7NDeNLuCzc6e86hc"),
                drive_to_direct("https://drive.google.com/uc?id=1wJFdsUkOTAKej6y1PjV80GjTZQyVwX7g"),
                drive_to_direct("https://drive.google.com/uc?id=1I8hRUCWRY-_a6pjpPapiT-AmBfzEJtD4"),
                drive_to_direct("https://drive.google.com/uc?id=1Nn2FamL9UUZe4nrrSIbwHQH-gGvzJLFU"),
                drive_to_direct("https://drive.google.com/uc?id=1n5Ocpv6oa6jfJm1hUPpKx_L15sGfMlWe"),
                drive_to_direct("https://drive.google.com/uc?id=1dG0M0F-J6igUEQh24qDu4T93DgHd3u1w"),
                drive_to_direct("https://drive.google.com/uc?id=1cib4JE2ox5SYGe4Ub61NdMcxQnMKyzAV"),
                drive_to_direct("https://drive.google.com/uc?id=1c37fx4w3oaLWM_cW5fZPtDgmKSADE0_g"),
                drive_to_direct("https://drive.google.com/uc?id=1CRqE5XvucBNXOOtWRdUAuqT5danW-pmH"),
                drive_to_direct("https://drive.google.com/uc?id=1pPKUyBEQXYHoRbRKJtSMCQAUcJcT2Vew")
            ]
        },
        {
            "name": "August Complex Fires",
            "location": "California – 2020",
            "video": drive_to_direct("https://drive.google.com/uc?id=1sq0ur4iDhUEjy8NrXrhJlwBxJxPAfvn4"),
            "text": drive_to_direct("https://drive.google.com/uc?id=16zZZgoG2-ycvQNs9cUb4NFjoONTFwEDW"),
            "right_images": [
                drive_to_direct("https://drive.google.com/uc?id=1gm0M7wkM_yviWjznv1lEINsB3B4Ppgtl"),
                drive_to_direct("https://drive.google.com/uc?id=1EDvaZdAXn6buoizeDq4Q277SyVnw7gSe"),
                drive_to_direct("https://drive.google.com/uc?id=1y7c2gPR2teGNV0SFew9brqB8pNuv-4kj"),
                drive_to_direct("https://drive.google.com/uc?id=1YEPniv5JGhF80i4xFcdZFvKMwO39Om0x")
            ],
            "slideshow": [
                drive_to_direct("https://drive.google.com/uc?id=1AVo4LLTcmOYpWOXZZ7tXrHdIO7RVRoeA"),
                drive_to_direct("https://drive.google.com/uc?id=1K6aBVY_TU80HvDw2-QwcHW6iGTR48R7j"),
                drive_to_direct("https://drive.google.com/uc?id=1PKGcZAxmstOr7oPpxK-d6C_aLCTB3G0x"),
                drive_to_direct("https://drive.google.com/uc?id=1lRNltHTSYYttxquT_CpVZ_UaOiiC0J5t"),
                drive_to_direct("https://drive.google.com/uc?id=1e5ffaTSXh_xZDD0kSK58H6jxl6ZlOVtx"),
                drive_to_direct("https://drive.google.com/uc?id=1HprSZ9ykepIAOz1lWgVGpbLHKEtPwUj5"),
                drive_to_direct("https://drive.google.com/uc?id=16g4xlUQa5hXa32btePltbARb-9meHH0y"),
                drive_to_direct("https://drive.google.com/uc?id=1tiA_iUSfr4AW6F0icLbZkNspQUJ4-JS1"),
                drive_to_direct("https://drive.google.com/uc?id=1O4LuE7MtAaTspxB9uU-iulu2nMuspYna"),
                drive_to_direct("https://drive.google.com/uc?id=1FJIdzML5k-1UNutZHdftbDSETF9tw7gR"),
                drive_to_direct("https://drive.google.com/uc?id=1ZHgOgxCELfV1S3HnRNW5ENNsVk5ETey0"),
                drive_to_direct("https://drive.google.com/uc?id=1X3ovjfScowapIjFCbiRe-EwzwehxDnWs")
            ]
        },
        {
            "name": "Australia Bushfires",
            "location": "Australia – 2019-2020",
            "video": drive_to_direct("https://drive.google.com/uc?id=12czFeITn06ATAbJ7Ctz595C2fmGPziKf"),
            "text": drive_to_direct("https://drive.google.com/uc?id=1fy3dPS8H33sher07ZLqyZA8RnDhnSMGn"),
            "right_images": [
                drive_to_direct("https://drive.google.com/uc?id=1qJZUrvYs-BwCM7M8Ae8F_VpuineW5RMs"),
                drive_to_direct("https://drive.google.com/uc?id=1wxvSGEiwv8xNO5Xcttls4AQ6nnSaQ8ov"),
                drive_to_direct("https://drive.google.com/uc?id=1Pl3Hnt13jjiTFRek2AvxySvAlc97Q8YF"),
                drive_to_direct("https://drive.google.com/uc?id=12UO9Pkfhc2ZL7IWJz5aake-AeKpBMrQg")
            ],
            "slideshow": [
                drive_to_direct("https://drive.google.com/uc?id=1PKGcZAxmstOr7oPpxK-d6C_aLCTB3G0x"),
                drive_to_direct("https://drive.google.com/uc?id=1lRNltHTSYYttxquT_CpVZ_UaOiiC0J5t"),
                drive_to_direct("https://drive.google.com/uc?id=1cib4JE2ox5SYGe4Ub61NdMcxQnMKyzAV"),
                drive_to_direct("https://drive.google.com/uc?id=1c37fx4w3oaLWM_cW5fZPtDgmKSADE0_g"),
                drive_to_direct("https://drive.google.com/uc?id=1CRqE5XvucBNXOOtWRdUAuqT5danW-pmH"),
                drive_to_direct("https://drive.google.com/uc?id=1pPKUyBEQXYHoRbRKJtSMCQAUcJcT2Vew")
            ]
        },
        {
            "name": "Black Saturday Bushfires",
            "location": "Australia – 2009",
            "video": drive_to_direct("https://drive.google.com/uc?id=14JekVKl12bTkHPdoiWZor9aOp9gF2B0P"),
            "text": drive_to_direct("https://drive.google.com/uc?id=1-wDod1INNQbK5PnoT78vqF6fY7ci_BIC"),
            "right_images": [
                drive_to_direct("https://drive.google.com/uc?id=1Gu1-PpRlQH18L8FUjqBSO0_wBQ_VWaP3"),
                drive_to_direct("https://drive.google.com/uc?id=1Ub5E7UFw1MX828StukzwTmeQApSUatcY"),
                drive_to_direct("https://drive.google.com/uc?id=1ajiVyDu4LgyvjqK62rpEg5ZTYYw7fn0Z"),
                drive_to_direct("https://drive.google.com/uc?id=18lsb3dKKxgA-FMdQI_awv8LfIVcxe5Pb")
            ],
            "slideshow": [
                drive_to_direct("https://drive.google.com/uc?id=1CPdU-kmxTkVHRKy2pLSLM7mq-IIMXX5X"),
                drive_to_direct("https://drive.google.com/uc?id=1HIkF8cpv3cvYDcOZA-sIgS89OPk8Pztk"),
                drive_to_direct("https://drive.google.com/uc?id=1DKRnP2lcfRnDKq8A6tHjSkZat7ZZ1g9R"),
                drive_to_direct("https://drive.google.com/uc?id=1AVwQb50Uu7Pz9JdpIaxtLG2B7SIomWuo"),
                drive_to_direct("https://drive.google.com/uc?id=1U-y2pTzVF1GOnvA94EGdz8pcMYPAOdnq"),
                drive_to_direct("https://drive.google.com/uc?id=1PqeNGvhPUGQ-9GgTmV5g8N9BvXl69vIX")
            ]
        },
        {
            "name": "Camp Fire",
            "location": "California – 2018",
            "video": drive_to_direct("https://drive.google.com/uc?id=1ydGLUFzzxlbFWekFBjEs6buckIWfvnAO"),
            "text": drive_to_direct("https://drive.google.com/uc?id=1206EFdEBJ78qUYQruCzzWGEO3qfrjDrJ"),
            "right_images": [
                drive_to_direct("https://drive.google.com/uc?id=1EaF8XMlQ_RjANgqPWQgwtCGQH_5h869s"),
                drive_to_direct("https://drive.google.com/uc?id=1jfW4_ZYTqRlsgmf_t8oMvmwMkn5x4ycB"),
                drive_to_direct("https://drive.google.com/uc?id=1fCCDNu8-aAUXH-_ypo_-WBw1lnHFofWi"),
                drive_to_direct("https://drive.google.com/uc?id=1Cvv3orcppCxF5HRTunsG_pQ53U4Sd6tb")
            ],
            "slideshow": [
                drive_to_direct("https://drive.google.com/uc?id=1xabuGO4L1Dk7cAIF-cIe66nfm7kf7w4f"),
                drive_to_direct("https://drive.google.com/uc?id=1V6cm7LS9HfyC9s_qrK6vbmOQiA_BYESZ"),
                drive_to_direct("https://drive.google.com/uc?id=15d4HWXk4LpbbLW5PqNT_YoXexgOA34-e"),
                drive_to_direct("https://drive.google.com/uc?id=1_PBBpo4Vf__Z8brTYlI3LXh9kmYXrYCV"),
                drive_to_direct("https://drive.google.com/uc?id=1oyooizCZpdccd5Kdn1EPwOqs7itpDOdP"),
                drive_to_direct("https://drive.google.com/uc?id=1DNIrhHiqTNJettlCliPZK6aG83U8RYCy")
            ]
        },
        {
            "name": "Chile Wildfires",
            "location": "2015",
            "video": drive_to_direct("https://drive.google.com/uc?id=1XpgUvyZ5B0JtSXuL6DJE9JgbL7qyuXsJ"),
            "text": drive_to_direct("https://drive.google.com/uc?id=1OBQT7uJtv8rppEhwB300KoO8MTrzMEpB"),
            "right_images": [
                drive_to_direct("https://drive.google.com/uc?id=1e2K55rj4xyioAYuz2zrZ_44nmcK6YoM-"),
                drive_to_direct("https://drive.google.com/uc?id=1euGvJc2emQm0UdgXy-PbbXdYHCzEAyqq"),
                drive_to_direct("https://drive.google.com/uc?id=1e8cp02wPvkMsB2VFUnAXWFl3JZFhYIfE"),
                drive_to_direct("https://drive.google.com/uc?id=1j6B-f1UIE1WStxkPunyp_laIxaRBd3_l")
            ],
            "slideshow": [
                drive_to_direct("https://drive.google.com/uc?id=1ra6ifOyR4uu30Mo2wlQqpeqnPpAjJMXy"),
                drive_to_direct("https://drive.google.com/uc?id=1dP4M4UkCWZQIkEBwKIuD--JkHNX7F-1a"),
                drive_to_direct("https://drive.google.com/uc?id=1ryuz8Ol9aLRbo9P3n0XIo07hfm14E0Hk"),
                drive_to_direct("https://drive.google.com/uc?id=1uOQEmfRFkcheST1vKO7kPmOvodKlHns8"),
                drive_to_direct("https://drive.google.com/uc?id=1SerrxgH1uytZ0JhAA3zI0IfVABXvNgyp"),
                drive_to_direct("https://drive.google.com/uc?id=1RfXMxRoVMk3_3o1aFJWXJ3c7aC2shlYo")
            ]
        },
        {
            "name": "Maui Wildfires",
            "location": "USA – 2023",
            "video": drive_to_direct("https://drive.google.com/uc?id=14ry2bpNu_-NFE4IkGuT7AskHYSoga0vq"),
            "text": drive_to_direct("https://drive.google.com/uc?id=1eqbXp38t9LYIjZirJhI8AYsd7g7u54eJ"),
            "right_images": [
                drive_to_direct("https://drive.google.com/uc?id=1wjzMB4KZ2FT_1Gw3DXwa-wsTA_kH9t2h"),
                drive_to_direct("https://drive.google.com/uc?id=13zf-qHskzMC2kg3sUbFGATQwIzeycxjd"),
                drive_to_direct("https://drive.google.com/uc?id=19_wmM8XBqh4SMekbJPYRk0xQyK415i78"),
                drive_to_direct("https://drive.google.com/uc?id=1uTqarXrIdLEokc0JSBuM1tJaDdaCKylM")
            ],
            "slideshow": [
                drive_to_direct("https://drive.google.com/uc?id=1RzVeB2ARf98rxk1daZHlSEb-Jc-1vezE"),
                drive_to_direct("https://drive.google.com/uc?id=1NE48YWMCeh0hqbj4IOQdZmi9m6eOljFj"),
                drive_to_direct("https://drive.google.com/uc?id=1gnztyLnqd4qoZsVgVgzyrZZIKbhXP28N"),
                drive_to_direct("https://drive.google.com/uc?id=1945Eph2JRjvI9szEuFi1IyVA_KXAihYk"),
                drive_to_direct("https://drive.google.com/uc?id=1OrBuHMDwtOhdjnpXoEnp9eEfpZK9tC5I")
            ]
        },
        {
            "name": "Texas Wildfires",
            "location": "2024",
            "video": drive_to_direct("https://drive.google.com/uc?id=1MwBMxlRMnsWeC7sPPQ0f9bGJNMad67dh"),
            "text": drive_to_direct("https://drive.google.com/uc?id=1DLqOyfA3r-EnJ4UfxnZdLJNyQ2UIysaJ"),
            "right_images": [
                drive_to_direct("https://drive.google.com/uc?id=1yipUU32d0Wm71jTHnzrHfIWt84qHFxS3"),
                drive_to_direct("https://drive.google.com/uc?id=1rVPDxdQBPsoSXJjIyeCdqwYb-vFXFzQ5"),
                drive_to_direct("https://drive.google.com/uc?id=1UbCWbGl5BOXVXuSbUwiEd2UHe7SOtcmM"),
                drive_to_direct("https://drive.google.com/uc?id=1RqzirDJjyHeP6XvEHO5sbzcbd-U8x8u3")
            ],
            "slideshow": [
                drive_to_direct("https://drive.google.com/uc?id=1Uzf-9GYSzqTHYNmMb7j4oCovn69G4-I3"),
                drive_to_direct("https://drive.google.com/uc?id=1BCHylrTpFx9dgqlrbZzmawRTed6fHcgo"),
                drive_to_direct("https://drive.google.com/uc?id=1x0fW3fN8brtnnrRG7yfOsEOVCHCj410W"),
                drive_to_direct("https://drive.google.com/uc?id=1tHZiCPvmh14sFyPkRY0wsFiTcxNztghz"),
                drive_to_direct("https://drive.google.com/uc?id=184-gBq9zHpes5ohaC6O0m0y5GZDA6QYt")
            ]
        },
        {
            "name": "Tubbs Fires",
            "location": "California – 2017",
            "video": drive_to_direct("https://drive.google.com/uc?id=1iGj3y6Aun134icA2Nq3OOXARdlf776mB"),
            "text": drive_to_direct("https://drive.google.com/uc?id=1P-tqu6hen2AFLtpDTOWkt6gegNjpM-gJ"),
            "right_images": [
                drive_to_direct("https://drive.google.com/uc?id=1BMTCybytO312yY3E-qyJXnRng9MB_VuJ"),
                drive_to_direct("https://drive.google.com/uc?id=1lLieYmZa32U4mAvUz6yRTv0GlbYFt9Bs"),
                drive_to_direct("https://drive.google.com/uc?id=1DRzg-cNMua2Nzr31-iDE-aDz1sYY5vOW"),
                drive_to_direct("https://drive.google.com/uc?id=1M6rrRZcDrdVC3sTwGMG7p3ZZfQ1p9Ofh")
            ],
            "slideshow": [
                drive_to_direct("https://drive.google.com/uc?id=1I49FgQEX04ZMZNsjReuUidOwEdJ0r6Wp"),
                drive_to_direct("https://drive.google.com/uc?id=1HC9n6KJJg5tyFaLNV-RS6QNefI-q9V_L"),
                drive_to_direct("https://drive.google.com/uc?id=1xYSc8ots7O4TOYalvXzFohDRxdYKYgZ8"),
                drive_to_direct("https://drive.google.com/uc?id=1dJEYZft1HBuBNl_qIWcCV8wv5uappbOl"),
                drive_to_direct("https://drive.google.com/uc?id=1rfMxko1q-GG-4gCf5gQXPHD5kRMtMXU1")
            ]
        },
        {
            "name": "Woolsey Fires",
            "location": "California – 2018",
            "video": drive_to_direct("https://drive.google.com/uc?id=1DNc08sxQs3w-VDuoVRdLlHaroOZz-o7O"),
            "text": drive_to_direct("https://drive.google.com/uc?id=1jBqamNrjXKOCteJMrFsNkwurYtigUBwH"),
            "right_images": [
                drive_to_direct("https://drive.google.com/uc?id=1M0GjWiC26mkm3Ys8grBAIvU1ONeI4dGa"),
                drive_to_direct("https://drive.google.com/uc?id=18gwJQHySECEpyZizsTfPUDK7DCxLekGA"),
                drive_to_direct("https://drive.google.com/uc?id=1YobiO_B_ehQrbTYI4-VvVmVy79ahdXZr"),
                drive_to_direct("https://drive.google.com/uc?id=12SUajfkP4zMfRCG2xm9xe2bG9Pa97Dct")
            ],
            "slideshow": [
                drive_to_direct("https://drive.google.com/uc?id=1blMNd5I418BGuStYFjrBaHzAKlZNKtfg"),
                drive_to_direct("https://drive.google.com/uc?id=1xabuGO4L1Dk7cAIF-cIe66nfm7kf7w4f"),
                drive_to_direct("https://drive.google.com/uc?id=1hKdV62RgRkTMble_vPnjSpGSEAkOeYwN"),
                drive_to_direct("https://drive.google.com/uc?id=1z-vYFdPlxtf4q_ztGyl6aWUblYgkjNxT"),
                drive_to_direct("https://drive.google.com/uc?id=1_Gg2ZglVKhiNG3BvSRJp_93REufTOjz9")
            ]
        }
       
    ]
}

# ----------------------------
# Optionally attempt to load remote txt (JSON) from a Drive link you provided.
# If you want to override the built-in events with a remote JSON file,
# set REMOTE_EVENTS_URL to a Google Drive link to the JSON (or raw JSON).
# The uploaded text file you mentioned (drive id 1kMJ...) can be used if it's JSON.
# If it isn't JSON, the script will keep the built-in 'disasters' above.
# ----------------------------
REMOTE_EVENTS_URL = None
# Example if you want to automatically load your uploaded file:
# REMOTE_EVENTS_URL = "https://drive.google.com/uc?id=1kMJfLUWxKP0XUfE77eeTy4cyI9jbDRcH"

def try_load_remote_events(url):
    global disasters
    if not url:
        return
    try:
        direct = drive_to_direct(url)
        r = requests.get(direct, timeout=20)
        r.raise_for_status()
        txt = r.text.strip()
        # Try JSON first
        try:
            obj = json.loads(txt)
            # Expecting same structure: {"Forest Fire": [ {...}, ... ]}
            if isinstance(obj, dict):
                disasters = obj
                print("Loaded remote disasters (JSON).")
                return
        except Exception:
            pass
        # Not JSON — don't override built-in; just print head for debug
        print("Remote file downloaded but not JSON. Keeping built-in events.")
    except Exception as e:
        print("Failed to load remote events:", e)

# Try load remote events at start if provided
try_load_remote_events(REMOTE_EVENTS_URL)

# ----------------------------
# OpenGL widget: sphere textured with current video frame
# ----------------------------
class VideoTextureGlobe(QOpenGLWidget):
    def __init__(self, video_path=None, parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.cap = None
        self.tex_id = None
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.zoom = -3.0
        self.auto_rotate = True
        self.dragging = False
        self.last_pos = None
        self.frame_counter = 0

        # timer to update frames & rotate
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(40)  # ~25 fps (texture updates throttled internally)

    def set_video(self, path):
        # close previous
        if self.cap:
            try:
                self.cap.release()
            except:
                pass
            self.cap = None
        self.video_path = path
        try:
            # OpenCV expects a filename
            self.cap = cv2.VideoCapture(path)
            if not self.cap.isOpened():
                print("Failed to open video:", path)
                self.cap = None
        except Exception as e:
            print("OpenCV open error:", e)
            self.cap = None

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        # Create texture
        if self.tex_id:
            try:
                glDeleteTextures([self.tex_id])
            except:
                pass
            self.tex_id = None
        self.tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.tex_id)
        # empty placeholder
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 2, 2, 0, GL_RGB, GL_UNSIGNED_BYTE, b'\xff\x00\xff'*4)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)
        glClearColor(0.0, 0.0, 0.0, 1.0)

    def resizeGL(self, w, h):
        if h == 0:
            h = 1
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / float(h), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, self.zoom)
        glRotatef(self.angle_x, 1.0, 0.0, 0.0)
        glRotatef(self.angle_y, 0.0, 1.0, 0.0)

        # Update texture from video if available, but throttle updates slightly for slowness
        if self.cap is not None:
            # read frame every few ticks to slow playback on the globe
            self.frame_counter += 1
            # change this divisor to slow down more (larger => slower)
            divisor = 4
            if self.frame_counter % divisor == 0:
                ret, frame = self.cap.read()
                if not ret:
                    # loop
                    try:
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = self.cap.read()
                    except:
                        ret = False
                if ret:
                    # convert BGR -> RGB, flip vertically (OpenGL expects bottom-to-top)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_rgb = cv2.flip(frame_rgb, 0)
                    h, w, _ = frame_rgb.shape
                    glBindTexture(GL_TEXTURE_2D, self.tex_id)
                    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, frame_rgb)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                    glBindTexture(GL_TEXTURE_2D, 0)

        # bind texture and draw sphere
        if self.tex_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.tex_id)
        else:
            glDisable(GL_TEXTURE_2D)

        quad = gluNewQuadric()
        gluQuadricTexture(quad, GL_TRUE)
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluSphere(quad, 1.0, 64, 64)

        if self.tex_id:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)

    def on_timer(self):
        if self.auto_rotate and not self.dragging:
            # reduce rotation speed for slower spinning
            self.angle_y += 0.03
            if self.angle_y > 360:
                self.angle_y -= 360
        self.update()

    # Interaction: drag to rotate, wheel to zoom
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.auto_rotate = False
            self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if not self.dragging or self.last_pos is None:
            return
        dx = event.x() - self.last_pos.x()
        dy = event.y() - self.last_pos.y()
        self.angle_y += dx * 0.5
        self.angle_x += dy * 0.5
        self.last_pos = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.auto_rotate = True
            self.last_pos = None

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120.0
        self.zoom += delta * 0.3
        self.zoom = max(-10.0, min(-1.0, self.zoom))
        self.update()

    def close(self):
        if self.cap:
            try:
                self.cap.release()
            except:
                pass
            self.cap = None
        super().close()

# ----------------------------
# Main App (layout + logic)
# ----------------------------
class DisasterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video-on-Globe Disaster Viewer")
        self.setGeometry(50, 50, 1400, 920)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # top controls
        top_layout = QHBoxLayout()
        self.disaster_dropdown = QComboBox()
        self.disaster_dropdown.addItems(disasters.keys())
        self.disaster_dropdown.currentTextChanged.connect(self.update_incidents)
        top_layout.addWidget(self.disaster_dropdown)

        self.incident_dropdown = QComboBox()
        self.update_incidents(self.disaster_dropdown.currentText())
        top_layout.addWidget(self.incident_dropdown)

        self.show_button = QPushButton("Show Incident")
        self.show_button.clicked.connect(self.show_incident)
        top_layout.addWidget(self.show_button)

        self.layout.addLayout(top_layout)

        # middle: left slideshow (0.5s) | globe | right slideshow (2s)
        middle_layout = QHBoxLayout()

        # left slideshow
        self.left_label = QLabel("Left Slideshow")
        self.left_label.setAlignment(Qt.AlignCenter)
        middle_layout.addWidget(self.left_label, 1)

        # center globe (video-textured)
        self.globe_widget = VideoTextureGlobe()
        middle_layout.addWidget(self.globe_widget, 1)

        # right slideshow
        self.right_label = QLabel("Right Slideshow")
        self.right_label.setAlignment(Qt.AlignCenter)
        middle_layout.addWidget(self.right_label, 1)

        self.layout.addLayout(middle_layout, 4)

        # text area (bigger)
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet("background-color:#111; color:white; font-size:15px;")
        self.layout.addWidget(self.text_area, 2)

        # timers and lists for slideshows
        self.left_images = []
        self.left_index = 0
        self.left_timer = QTimer()
        self.left_timer.timeout.connect(self.next_left_image)
        self.left_timer.setInterval(500)

        self.right_images = []
        self.right_index = 0
        self.right_timer = QTimer()
        self.right_timer.timeout.connect(self.next_right_image)
        self.right_timer.setInterval(2000)

        # Keep track of downloaded files to optionally clean up
        self.downloaded_files = []

    def update_incidents(self, disaster_type):
        incidents = disasters.get(disaster_type, [])
        names = [f"{i.get('name','Unknown')} — {i.get('location','')}" for i in incidents]
        self.incident_dropdown.clear()
        self.incident_dropdown.addItems(names)
        if names:
            self.incident_dropdown.setCurrentIndex(0)

    def show_incident(self):
        # get selected incident
        dtype = self.disaster_dropdown.currentText()
        idx = self.incident_dropdown.currentIndex()
        if idx < 0:
            return
        incident = disasters[dtype][idx]

        # 1) download and set globe video
        video_url = incident.get("video")
        if video_url:
            out_video = "incident_globe.mp4"
            ok = download_file(drive_to_direct(video_url), out_video)
            if ok and os.path.exists(out_video):
                # store for cleanup
                if out_video not in self.downloaded_files:
                    self.downloaded_files.append(out_video)
                self.globe_widget.set_video(out_video)
            else:
                self.text_area.setPlainText("Failed to download globe video.")
        else:
            self.text_area.setPlainText("No video provided for this incident.")

        # 2) download and set description
        self.text_area.setPlainText("Loading description...")
        text_url = incident.get("text")
        desc = "No description available."
        if text_url:
            out_txt = "incident_desc.txt"
            ok = download_file(drive_to_direct(text_url), out_txt)
            if ok and os.path.exists(out_txt):
                try:
                    with open(out_txt, "r", encoding="utf-8") as f:
                        desc = f.read()
                except Exception as e:
                    desc = f"Error reading description: {e}"
                if out_txt not in self.downloaded_files:
                    self.downloaded_files.append(out_txt)
            else:
                desc = "Failed to download description."
        self.text_area.setPlainText(desc)
        self.highlight_text()

        # 3) left slideshow (0.5s)
        self.left_timer.stop()
        self.left_images.clear()
        self.left_index = 0
        for i, url in enumerate(incident.get("slideshow", [])):
            out = f"left_{i}.jpg"
            if download_file(drive_to_direct(url), out):
                pix = QPixmap(out)
                if not pix.isNull():
                    self.left_images.append(pix)
                    if out not in self.downloaded_files:
                        self.downloaded_files.append(out)
        if self.left_images:
            self.left_timer.start()

        # 4) right slideshow (2s)
        self.right_timer.stop()
        self.right_images.clear()
        self.right_index = 0
        for i, url in enumerate(incident.get("right_images", [])):
            out = f"right_{i}.jpg"
            if download_file(drive_to_direct(url), out):
                pix = QPixmap(out)
                if not pix.isNull():
                    self.right_images.append(pix)
                    if out not in self.downloaded_files:
                        self.downloaded_files.append(out)
        if self.right_images:
            self.right_timer.start()

    def next_left_image(self):
        if not self.left_images:
            return
        pix = self.left_images[self.left_index]
        self.left_label.setPixmap(pix.scaled(
            self.left_label.width(), self.left_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.left_index = (self.left_index + 1) % len(self.left_images)

    def next_right_image(self):
        if not self.right_images:
            return
        pix = self.right_images[self.right_index]
        self.right_label.setPixmap(pix.scaled(
            self.right_label.width(), self.right_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.right_index = (self.right_index + 1) % len(self.right_images)

    def highlight_text(self):
        cursor = self.text_area.textCursor()
        full = self.text_area.toPlainText()

        # reset formatting
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())
        cursor.clearSelection()

        # highlight "human impacts" yellow + black fg (and 'human' or 'impacts')
        fmt_h = QTextCharFormat()
        fmt_h.setBackground(QColor("yellow"))
        fmt_h.setForeground(QColor("black"))
        for m in re.finditer(r"\b(human|impacts|human impacts)\b", full, re.IGNORECASE):
            s, e = m.start(), m.end()
            cursor.setPosition(s)
            cursor.setPosition(e, QTextCursor.KeepAnchor)
            cursor.mergeCharFormat(fmt_h)

        # highlight numbers cyan + black fg
        fmt_n = QTextCharFormat()
        fmt_n.setBackground(QColor("cyan"))
        fmt_n.setForeground(QColor("black"))
        for m in re.finditer(r"\d+(\.\d+)?", full):
            s, e = m.start(), m.end()
            cursor.setPosition(s)
            cursor.setPosition(e, QTextCursor.KeepAnchor)
            cursor.mergeCharFormat(fmt_n)

    def closeEvent(self, event):
        # Clean up downloaded files if you want (uncomment to remove):
        # for f in self.downloaded_files:
        #     try: os.remove(f)
        #     except: pass
        super().closeEvent(event)

# ----------------------------
# Run application
# ----------------------------
def main():
    app = QApplication(sys.argv)
    w = DisasterApp()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


