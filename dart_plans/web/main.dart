import 'dart:html';

final String localLocation = Uri.decodeFull(window.location.toString());
final String prefix = makePrefix();

Element projectTitle = querySelector('#project-title');
Element projectTitleButton = querySelector('#proj-title-btn');
Element projectTitleDialog = querySelector('#proj-title-dialog');
Element projectTitleInput = querySelector('#proj-title-input');
Element projectTitleCancel = querySelector('#proj-title-cancel');

/// 初始化一些东西, 比如给一些按钮添加事件.
void init() {
  projectTitleButton.onClick.listen((_) {
    projectTitle.setAttribute('hidden', '');
    projectTitleDialog.removeAttribute('hidden');
    projectTitleInput.focus();
  });
  projectTitleCancel.onClick.listen((e) {
    e.preventDefault();
    projectTitle.removeAttribute('hidden');
    projectTitleDialog.setAttribute('hidden', '');
  });
}

void main() {
  init();
  window.console.log(prefix);
}

String makePrefix() {
  var re = RegExp(r'[/\\:]'); // '/', '\' and ':'
  var prefix = localLocation.replaceAll(re, '');
  prefix = prefix.substring('fileC'.length, prefix.length - '.html'.length);
  var len = prefix.length;
  if (len > 40) {
    // 取该字符串的头和尾组成 prefix (为了尽可能避免重复, 又不能太长)
    // 共 40 个字符, 相当于 SHA-1 长度.
    // 本来是计算 SHA-1 的, 但为了与旧版 (JavaScript版本) 保持一致.
    prefix = prefix.substring(0, 20) + prefix.substring(len - 20);
  }
  return prefix;
}
