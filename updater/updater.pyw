import base64
import json
import os
import shutil
import zipfile

from appJar import gui

file_list = []
base_dir = os.path.dirname(os.path.abspath(__file__))
cfg_path = os.path.join(base_dir, "updater.cfg")
temp_file_path = os.path.join(base_dir, "small-plans.zip")
small_plans_html = os.path.join(base_dir, "small-plans.html")
zip_url = "https://github.com/ahui2016/small-plans/raw/master/releases/small-plans.zip"
api_url = "https://api.github.com/repos/ahui2016/small-plans/contents/small-plans.html"

if os.path.exists(cfg_path):
    with open(cfg_path, encoding='utf-8') as cfg_file:
        for line in cfg_file:
            file_list.append(line.strip())


def add_to_list():
    file_path = app.getEntry("选择文件")
    if not os.path.exists(file_path):
        app.popUp("File Not Exists", message="文件不存在", kind="warning")
        return
    if not (file_path.endswith(".html") or file_path.endswith(".htm")):
        app.popUp("Not HTML", message="只能添加 html 文件", kind="warning")
        return
    with open(cfg_path, mode='a', encoding='utf-8') as cfg_file_a:
        cfg_file_a.write(file_path + '\n')
    app.addListItem("files", file_path)


def delete_item():
    selected = app.getListBoxPos("files")
    if len(selected) > 0:
        app.removeListItemAtPos("files", selected[0])
        all_items = app.getAllListItems("files")
        with open(cfg_path, mode='w', encoding='utf-8') as cfg_file_w:
            for item in all_items:
                cfg_file_w.write(item + '\n')


def update():
    from urllib import request
    try:
        app.popUp("点击确定开始更新, 处理过程中本窗口会卡住, 请耐心等待")
        with request.urlopen(api_url) as resp:
            resp_obj = json.load(resp)
            file_content = base64.standard_b64decode(resp_obj["content"])
            with open(small_plans_html, mode='wb') as html_file:
                html_file.write(file_content)
            return
        # request.urlretrieve(zip_url, temp_file_path)
        # with zipfile.ZipFile(temp_file_path) as zip_file:
        #     for file_name in zip_file.namelist():
        #         if file_name == "small-plans.html":
        #             zip_file.extract(file_name, small_plans_html)
        app.statusbar(text="下载成功")
    except Exception as err:
        app.statusbar(text="下载失败, 更新文件: 0")
        app.popUp("下载失败", message=err, kind="error")
        return

    ok_count = 0
    ng_count = 0
    all_items = app.getAllListItems("files")
    for item in all_items:
        if not os.path.exists(item):
            msg = "文件不存在\n" + item
            app.popUp("File Not Exists", message=msg, kind="warning")
            ng_count += 1
            continue
        with open(item, encoding='utf-8') as cfg_file_update:
            first_line = cfg_file_update.readline()
            if first_line.find('<!--small-plans.html-->') < 0:
                msg = "目标文件可能不是 small-plans 源文件: " + \
                      item + "\n" + \
                      "(目标文件的第一行必须是: <!--small-plans.html-->)"
                app.popUp("Update Fail", message=msg, kind="warning")
                ng_count += 1
                continue
        try:
            shutil.copyfile(small_plans_html, item)
            ok_count += 1
        except Exception as err:
            app.popUp("Error", message=err)
            ng_count += 1

    app.statusbar(text="更成结果: 成功: %d, 失败: %d" % (ok_count, ng_count))


with gui("更新助手", "640x450", font={'size': 10, 'family': 'Microsoft YaHei UI'}) as app:
    app.setPadding([0, 20])
    current_row = 0
    app.label("更新助手\nan updater for small-plans", column=1, colspan=2, sticky="w")

    app.setPadding([0, 0])
    current_row += 1
    app.label('请先选择文件, 然后点击"添加"按钮', row=current_row, column=1, colspan=2)

    current_row += 1
    app.entry("选择文件", kind="open", row=current_row, column=1, colspan=2, sticky="ew")
    app.button("添加", add_to_list, row=current_row, column=3, sticky="")

    app.setPadding([0, 20])
    current_row += 1
    app.separator(row=current_row, colspan=4, sticky="ew")

    app.setPadding([0, 0])
    current_row += 1
    app.label("已添加:", row=current_row, column=1, sticky="w")

    current_row += 1
    app.listbox("files", value=file_list, rows=5, row=current_row, column=1, colspan=2, sticky="ew")
    app.button("删除", delete_item, row=current_row, column=3, sticky="")

    app.setPadding([0, 20])
    current_row += 1
    app.label('点击 "更新" 按钮即可批量更新', row=current_row, column=1, sticky="e")
    app.button("更新", update, row=current_row, column=3, sticky="")

    app.setPadding([0, 0])
    current_row += 1
    app.statusbar(
        text="提示: 点击更新按钮, 将会自动从 GitHub 下载最新版本覆盖如上所示的已添加文件"
    )
