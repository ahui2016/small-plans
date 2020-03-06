from appJar import gui


def add_to_list():
    file_path = app.getEntry("选择文件")
    app.addListItem("files", file_path)


def delete_item():
    selected = app.getListBoxPos("files")
    if len(selected) > 0:
        app.removeListItemAtPos("files", selected[0])


with gui("更新助手", "640x450", font={'size': 10, 'family': 'Microsoft YaHei UI'}) as app:
    app.setPadding([0, 20])
    current_row = 0
    app.label("更新助手\nan updater for small-plans", colspan=2, sticky="w")

    app.setPadding([0, 0])
    current_row += 1
    app.label('请先选择文件, 然后点击"添加"按钮', row=current_row, column=1, colspan=2, sticky="w")

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
    app.listbox("files", rows=5, row=current_row, column=1, colspan=2, sticky="ew")
    app.button("删除", delete_item, row=current_row, column=3, sticky="")

    app.setPadding([0, 20])
    current_row += 1
    app.label('点击 "更新" 按钮即可批量更新', row=current_row, column=1, sticky="e")
    app.button("更新", row=current_row, column=3, sticky="")

    app.setPadding([0, 0])
    current_row += 1
    app.statusbar(
        text="提示: 点击更新按钮, 将会自动从 GitHub 下载最新版本覆盖如上所示的已添加文件"
    )
