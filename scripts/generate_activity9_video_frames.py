from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SCREENS = ROOT / "output" / "manual" / "screens"
FRAMES = ROOT / "output" / "video" / "frames"
FONT_REG = "/Users/thanthita.korn/Library/Fonts/THSarabunNew.ttf"
FONT_BOLD = "/Users/thanthita.korn/Library/Fonts/THSarabunNew Bold.ttf"

W, H = 1920, 1080
NAVY = "#102A56"
BLUE = "#1C5F98"
GOLD = "#D5A335"
LIGHT = "#F2F6FA"
TEXT = "#182C43"
MUTED = "#617489"
WHITE = "#FFFFFF"
GREEN = "#2A7C56"


def font(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def wrap_thai(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        words = paragraph.split(" ")
        line = ""
        for word in words:
            trial = word if not line else line + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                line = trial
                continue
            if line:
                lines.append(line)
            if draw.textlength(word, font=fnt) <= max_width:
                line = word
                continue
            chunk = ""
            for ch in word:
                trial_chunk = chunk + ch
                if draw.textlength(trial_chunk, font=fnt) > max_width and chunk:
                    lines.append(chunk)
                    chunk = ch
                else:
                    chunk = trial_chunk
            line = chunk
        if line:
            lines.append(line)
    return lines


def draw_wrapped(draw, xy, text, fnt, fill, max_width, line_height, max_lines=None):
    x, y = xy
    lines = wrap_thai(draw, text, fnt, max_width)
    if max_lines:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_height
    return y


def rounded(draw, box, fill, outline=None, radius=26, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def screen_panel(base: Image.Image, filename: str | None):
    if not filename:
        return
    path = SCREENS / filename
    if not path.exists():
        return
    panel = (680, 110, 1870, 985)
    draw = ImageDraw.Draw(base)
    rounded(draw, panel, WHITE, "#D7E1EB", radius=28, width=3)
    shot = Image.open(path).convert("RGB")
    contained = ImageOps.contain(shot, (panel[2] - panel[0] - 38, panel[3] - panel[1] - 38), Image.Resampling.LANCZOS)
    x = panel[0] + (panel[2] - panel[0] - contained.width) // 2
    y = panel[1] + (panel[3] - panel[1] - contained.height) // 2
    base.paste(contained, (x, y))


def make_slide(index: int, total: int, title: str, bullets: list[str], screen: str | None, section: str):
    img = Image.new("RGB", (W, H), LIGHT)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 70), fill=NAVY)
    draw.text((72, 19), "E-CMIS · กิจกรรมที่ 9 ระบบหมายจับ", font=font(34, True), fill=WHITE)
    draw.text((W - 260, 21), f"{index:02d} / {total:02d}", font=font(31, True), fill="#D7E7F7")

    draw.text((74, 112), section, font=font(28, True), fill=GOLD)
    y = draw_wrapped(draw, (72, 160), title, font(55, True), NAVY, 540, 61, max_lines=3)
    draw.rectangle((72, y + 8, 160, y + 15), fill=GOLD)
    y += 46
    for item in bullets:
        rounded(draw, (72, y + 4, 105, y + 37), BLUE, radius=16)
        draw.text((83, y + 2), "•", font=font(31, True), fill=WHITE)
        y = draw_wrapped(draw, (122, y), item, font(29), TEXT, 515, 36, max_lines=3)
        y += 18
    screen_panel(img, screen)

    draw.line((72, 1025, W - 72, 1025), fill="#CCD8E4", width=2)
    draw.text((72, 1037), "Mockup สำหรับยืนยันกระบวนงาน — ไม่มี Police API · AWIS อยู่ระหว่าง MOU", font=font(25), fill=MUTED)
    FRAMES.mkdir(parents=True, exist_ok=True)
    img.save(FRAMES / f"frame-{index:02d}.png", quality=95)


def make_cover(index: int, total: int, closing=False):
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    draw.ellipse((1320, -260, 2150, 570), fill="#153A70")
    draw.ellipse((-270, 700, 520, 1490), fill="#143465")
    draw.rectangle((132, 165, 158, 850), fill=GOLD)
    label = "สรุปการใช้งาน" if closing else "วิดีโอสาธิตการใช้งาน"
    draw.text((205, 190), label, font=font(42, True), fill=GOLD)
    y = draw_wrapped(draw, (205, 280), "ระบบฐานข้อมูล\nการดำเนินการตามหมายจับ", font(82, True), WHITE, 1240, 92)
    draw_wrapped(draw, (210, y + 40), "E-CMIS กิจกรรมที่ 9", font(45), "#D9E6F2", 800, 52)
    summary = (
        "ครบตั้งแต่รับงานจากกิจกรรมที่ 5 จัดทำคำร้อง ยื่นศาล บันทึกหมาย ส่งตำรวจ "
        "ติดตามผล จับกุม ยุติ/ถอนหมาย แจ้งทะเบียนกลาง และรายงานผู้บริหาร"
        if not closing else
        "ทุกงานใช้เลขงานและเอกสารชุดเดียวกัน เก็บ Version และ Audit Trail "
        "รองรับ Manual ก่อนเปิด AWIS และไม่บันทึกถอนหมายจนกว่าศาลมีคำสั่ง"
    )
    draw_wrapped(draw, (210, y + 140), summary, font(37), "#EAF1F8", 1240, 50, max_lines=4)
    draw.text((205, 944), f"ฉบับสาธิตวันที่ 16 สิงหาคม 2569 · {index:02d}/{total:02d}", font=font(30), fill="#BDCCE0")
    FRAMES.mkdir(parents=True, exist_ok=True)
    img.save(FRAMES / f"frame-{index:02d}.png", quality=95)


slides = [
    ("จุดเริ่มต้นมาจากกิจกรรมที่ 5", ["กิจกรรมที่ 5 ส่งสำนวน ผู้ถูกกล่าวหา ข้อกล่าวหา และพยานหลักฐานเข้ามา", "บันทึกผลหรือหนังสือจากอัยการแล้วเปิดงานขอหมายจับ", "ข้อมูลเชื่อมกันภายใน E-CMIS ไม่คีย์สำนวนซ้ำ"], "02-registry.png", "เริ่มงาน"),
    ("ทะเบียนคำร้องคือทะเบียนกลาง", ["ค้นหาด้วยเลขงาน เลขสำนวน ชื่อ หรือหน่วยงาน", "แสดงเฉพาะขั้นจัดทำคำร้อง ไม่ปะปนงานติดตามหลังศาลออกหมาย", "ส่งงานให้ผู้จัดทำหรือเจ้าของสำนวนโดยไม่สร้างคำร้องซ้ำ"], "02-registry.png", "ทะเบียนคำร้อง"),
    ("งานของเจ้าหน้าที่/เจ้าของสำนวน", ["แบ่งแท็บตามขั้นตอน ตรวจแก้ รอผู้บังคับบัญชา รอ ผอ. พร้อมยื่น และรอศาล", "เปิดงานแล้วเห็นข้อมูลสำนวนและเอกสารทั้งหมด", "มีตัวกรองขั้นสูงและผู้รับผิดชอบขั้นตอนปัจจุบัน"], "03-officer-queue.png", "คิวงาน"),
    ("จัดทำคำร้อง ปปท.8-17", ["กรอกแบบในระบบให้สร้าง Word/PDF หรืออัปโหลดคำร้องที่ทำภายนอก", "ตรวจข้อมูลผู้ร้อง ผู้ถูกกล่าวหา พฤติการณ์ ฐานความผิด และเหตุออกหมาย", "แนบหนังสืออัยการและพยานหลักฐานจากกิจกรรมที่ 5"], "04-request-form.png", "จัดทำคำร้อง"),
    ("ตรวจภายในและสร้างชุดยื่นศาล", ["เจ้าของสำนวน ผู้บังคับบัญชา และ ผอ.สำนัก/กองตรวจตามสายงาน", "เลือกเฉพาะเอกสารที่จะยื่นจริง เอกสารภายในไม่ติดไปศาล", "ทุกครั้งที่แก้ไขสร้าง Version และเก็บรอบเดิม"], "05-court-package.png", "ก่อนยื่นศาล"),
    ("ยื่นศาลแบบ Manual ก่อน", ["AWIS อยู่ระหว่างขอ MOU จึงปิดตัวเลือกไว้", "ดาวน์โหลดหรือพิมพ์ชุดเอกสารแล้วนำไปยื่นศาล", "กลับมาบันทึกศาล วันที่ยื่น เลขรับ และหลักฐานรับคำร้อง"], "05-court-package.png", "ช่องทางศาล"),
    ("รองรับผลศาลทุกกรณี", ["ออกหมาย ขอแก้ไข นัดไต่สวน โอนศาล ไม่อนุมัติ หรือถอนคำร้อง", "ขอแก้ไขจะส่งกลับเจ้าของสำนวนและสร้างชุดยื่นครั้งใหม่", "เลขรับคำร้องไม่ใช่เลขหมายจับ"], "03-officer-queue.png", "ผลพิจารณา"),
    ("ตรวจหมายจับฉบับศาล", ["เปิดดูหมายและเอกสารทุกฉบับก่อนยืนยัน", "ตรวจเลขหมาย บุคคล ศาล คดี วันที่ออก และอายุความ", "ถูกต้องแล้วส่งชุดข้อมูลเดียวกันให้ธุรการคดี กอท."], "06-warrant-verification.png", "หลังศาลออกหมาย"),
    ("ธุรการคดี กอท. รับช่วง", ["ตรวจรับเอกสาร ลงทะเบียนคุม และจัดทำหนังสือนำส่ง", "ถ้าไม่ครบส่งกลับเจ้าของสำนวนพร้อมรายการแก้ไข", "ขั้นตอนต่อเนื่อง ไม่เด้งกลับคิวระหว่างทำงาน"], "07-got-queue.png", "งาน กอท."),
    ("ส่งหมายให้ตำรวจอย่างเป็นทางการ", ["ไม่มี API เชื่อมระบบตำรวจ", "เลือกไปรษณีย์หรือนำส่งด้วยตนเองและแนบหลักฐาน", "หนังสือนำส่งใช้ข้อมูลเดิม ไม่กรอกข้อมูลหมายซ้ำ"], "07-got-queue.png", "นำส่งตำรวจ"),
    ("Tracking ไปรษณีย์ทำงานอัตโนมัติ", ["ระบบดึงสถานะรับฝาก ขนส่ง ออกนำจ่าย สำเร็จ ไม่สำเร็จ และตีกลับ", "ผู้ใช้ไม่ต้องเข้ามากดเช็กเลขพัสดุเอง", "เมื่อนำจ่ายสำเร็จ เปิดงานติดตามหมายและแจ้งผู้รับผิดชอบ"], "08-tracking.png", "ติดตามการนำจ่าย"),
    ("เลือกรูปแบบจับกุมในช่วงติดตาม", ["ตำรวจจับเอง", "ป.ป.ท. กับตำรวจร่วมจับ หรือเจ้าของสำนวนร่วมจับ", "ป.ป.ท. จับเอง และสามารถแก้แผนเมื่อสถานการณ์เปลี่ยน"], "08-tracking.png", "แผนปฏิบัติการ"),
    ("บันทึกผลปฏิบัติการ", ["จับกุม ไม่พบตัว หลบหนี ต่อสู้ มอบตัว อายัดตัว ตาย หรือขาดอายุความ", "แนบวันเวลา สถานที่ หน่วยปฏิบัติ บันทึกจับกุม และเหตุการณ์", "ถ้าจับได้ให้บันทึกการส่งตัวอัยการและใบรับตัว"], "08-tracking.png", "ผลตามหมาย"),
    ("ตรวจเหตุและเสนอขอยุติ", ["ใช้หลักฐานตามเหตุ: จับกุม มอบตัว มรณบัตร อายุความ หรือคำสั่งศาล", "กอท. จัดชุดเสนอโดยอ้างหมายและสำนวนเดิม", "หากหลักฐานไม่ครบ งานอยู่รอตรวจและยังไม่ส่งอนุมัติ"], "09-approval.png", "ยุติการบังคับ"),
    ("ผู้มีอำนาจพิจารณา", ["เลือกอนุมัติ ขอข้อมูลเพิ่ม หรือไม่อนุมัติ", "บันทึกเลขอ้างอิง วันที่ ความเห็น และหนังสือฉบับลงนาม", "ไม่อนุมัติจะคืนหมายกลับเข้าสู่งานติดตาม"], "09-approval.png", "ผลอนุมัติ"),
    ("แจ้งยุติให้ตำรวจและสำนัก/กอง", ["กอท. จัดหนังสือหลังได้รับอนุมัติ", "ส่งตำรวจทางไปรษณีย์หรือนำส่งด้วยตนเอง", "ขั้นนี้ยังไม่ใช่ถอนหมายแล้ว ต้องรอคำสั่งศาล"], "10-termination-notice.png", "หนังสือแจ้งยุติ"),
    ("สำนัก/กองรายงานศาลถอนหมาย", ["ยื่นหนังสือรายงานพร้อมผลอนุมัติและหลักฐาน", "บันทึกเลขรับและผลศาลแบบ Manual ระหว่างยังไม่เชื่อม AWIS", "ศาลขอเอกสารเพิ่มจะเก็บเลขรับเดิมและสร้างรอบยื่นใหม่"], "11-bureau-court.png", "ถอนหมาย"),
    ("ถอนหมายเมื่อศาลมีคำสั่งเท่านั้น", ["บันทึกเลขคำสั่ง วันที่ ไฟล์ และเหตุถอน", "แจ้งตำรวจ กอท. เจ้าของสำนวน สำนัก/กอง และหน่วยงานที่เกี่ยวข้อง", "หยุดงานติดตามและเก็บเอกสารไว้ตรวจสอบย้อนหลัง"], "11-bureau-court.png", "ปิดหมาย"),
    ("ครบ 180 วัน แจ้งทะเบียนกลาง", ["ระบบคำนวณจากวันที่ออกหมายและตรวจว่ายังมีผล/ยังจับไม่ได้", "บันทึกว่า ‘แจ้งแล้ว’ ไม่สรุปว่าย้ายสำเร็จ", "หลังแจ้งแล้วหมายยังอยู่ในงานติดตาม"], "12-central-registry.png", "ทะเบียนบ้านกลาง"),
    ("รายงานและนำเข้าข้อมูลเก่า", ["Dashboard Real-time กรอง Drill-down และ Export Word Excel PDF", "รายงานหมายค้าง จับได้ ขาดอายุความ เสียชีวิต และใกล้ขาด", "นำเข้าข้อมูล EVA/PCMS พร้อมตรวจซ้ำ ก่อนเลิกใช้ระบบเดิม"], "13-reports.png", "รายงานผู้บริหาร"),
]


def build():
    FRAMES.mkdir(parents=True, exist_ok=True)
    for old in FRAMES.glob("frame-*.png"):
        old.unlink()
    total = len(slides) + 2
    make_cover(1, total)
    for idx, (title, items, screen, section) in enumerate(slides, 2):
        make_slide(idx, total, title, items, screen, section)
    make_cover(total, total, closing=True)
    print(FRAMES)


if __name__ == "__main__":
    build()
