import base64
import json
import os
import shutil

from appJar import gui

file_list = []
base_dir = os.path.dirname(os.path.abspath(__file__))
cfg_path = os.path.join(base_dir, "updater.cfg")
small_plans_html = os.path.join(base_dir, "small-plans.html")
raw_url = "https://give-me-five.coding.net/p/small-plans/d/small-plans/git/raw/master/small-plans.html"

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
    app.text("result", "开始下载...\n", replace=True)
    from urllib import request
    try:
        request.urlretrieve(raw_url, small_plans_html)
        app.text("result", "\n下载成功!\n")
    except Exception as err:
        app.text("result", "\n下载失败!\n")
        app.text("result", "\n%s\n" % str(err))
        app.text("result", "\n未更新任何文件.\n")
        app.popUp("下载失败", message=err, kind="error")
        return

    app.text("result", "\n开始更新...\n")
    all_items = app.getAllListItems("files")
    for item in all_items:
        if not os.path.exists(item):
            app.text("result", "\n文件不存在:\n%s\n" % item)
            continue
        with open(item, encoding='utf-8') as cfg_file_update:
            first_line = cfg_file_update.readline()
            if first_line.find('<!--small-plans.html-->') < 0:
                app.text("result", "\n不是 small-plans 源文件:\n%s\n" % item)
                continue
        try:
            shutil.copyfile(small_plans_html, item)
            app.text("result", "\n更新成功:\n%s\n" % item)
        except Exception as err:
            app.text("result", "\n%s:\n%s\n" % (err, item))
    app.popUp("Update Finished", message="更新结束，请查看消息栏")


with gui("更新助手", "600x550", font={'size': 10, 'family': 'Microsoft YaHei UI'}) as app:
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
    app.listbox("files", value=file_list, rows=current_row, row=current_row, column=1, colspan=2, sticky="ew")
    app.button("删除", delete_item, row=current_row, column=3, sticky="")

    app.setPadding([0, 20])
    current_row += 1
    app.label('点击 "更新" 按钮即可批量更新', row=current_row, column=1, sticky="e")
    app.button("更新", update, row=current_row, column=3, sticky="")

    app.setPadding([20, 0])
    current_row += 1
    app.label("消息栏", row=current_row, colspan=4, sticky="w")

    app.setPadding([20, 0])
    current_row += 1
    tips = "\n提示: 点击更新按钮, 将会自动从 GitHub 下载最新版本覆盖如上所示的已添加文件"
    app.text("result", value=tips, scroll=True, height=7, font=10, row=current_row, colspan=4, sticky="ew")

    current_row += 1
    app.label(" ", row=current_row, colspan=4)
