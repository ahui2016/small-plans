import 'dart:async';
import 'dart:html';

final String localLocation = Uri.decodeFull(window.location.toString());
final String workingDir = makeWorkingDir(localLocation);
final String prefix = makePrefix(localLocation);
final String projectTitleKey = '$prefix-projectTitle';
final String descriptionKey = '$prefix-projectDescription';

Element browserTabTitle = querySelector('title');
Element projectTitleSection = querySelector('#proj-title-section');
Element projectTitle = querySelector('#project-title');
Element projectDescription = querySelector('#proj-description');
Element projectTitleDialog = querySelector('#proj-title-dialog');
InputElement projectTitleInput = querySelector('#proj-title-input');
TextAreaElement descriptionInput = querySelector('#description-input');

Element exportImportButtons = querySelector('#export-import-buttons');
Element importDialog = querySelector('#import-dialog');
InputElement importDir = querySelector('#import-dir');
Element exportDialog = querySelector('#export-dialog');
InputElement exportDir = querySelector('#export-dir');

/// 初始化一些东西, 比如给一些按钮添加事件.
void init() {
  initTitleDescription();
  initExportDialog();
  initImportDialog();
}

void main() {
  init();
  window.console.log(prefix);
}

/// 注意每当修改 `window.localStorage[projectTitleKey]` 的时候, 都要避免其值为空字符串,
/// 如果其值为空字符串, 则自动设为 'Small Plans'.
void initTitleDescription() {
  window.localStorage[projectTitleKey] ??= 'Small Plans';
  projectTitle.text = window.localStorage[projectTitleKey];
  browserTabTitle.text = projectTitle.text;
  projectDescription.text = window.localStorage[descriptionKey];

  querySelector('#proj-title-btn').onClick.listen((_) {
    projectTitleInput.value = window.localStorage[projectTitleKey];
    descriptionInput.value = window.localStorage[descriptionKey];
    projectTitleSection.setAttribute('hidden', '');
    projectTitleDialog.removeAttribute('hidden');
    projectTitleInput.focus();
  });

  querySelector('#proj-title-cancel').onClick.listen((e) {
    e.preventDefault();
    projectTitleSection.removeAttribute('hidden');
    projectTitleDialog.setAttribute('hidden', '');
  });

  querySelector('#proj-title-ok').onClick.listen((e) {
    e.preventDefault();
    projectTitle.text = projectTitleInput.value.trim();
    if (projectTitle.text.isEmpty) projectTitle.text = 'Small Plans';
    window.localStorage[projectTitleKey] = projectTitle.text;
    browserTabTitle.text = projectTitle.text;
    projectDescription.text = descriptionInput.value.trim();
    window.localStorage[descriptionKey] = projectDescription.text;
    projectTitleSection.removeAttribute('hidden');
    projectTitleDialog.setAttribute('hidden', '');
  });
}

void initExportDialog() {
  querySelector('#export-button').onClick.listen((e) {
    e.preventDefault();
    exportImportButtons.setAttribute('hidden', '');
    exportDialog.removeAttribute('hidden');
  });

  exportDir.value = workingDir;

  querySelector('#export-copy-btn').onClick.listen((e) {
    e.preventDefault();

    Future(() {
      exportDir.select();
    }).then((_) {
      window.document.execCommand('copy');
    });
  });

  querySelector('#export-dialog-close').onClick.listen((e) {
    e.preventDefault();
    exportImportButtons.removeAttribute('hidden');
    exportDialog.setAttribute('hidden', '');
  });

}

void initImportDialog() {
  querySelector('#import-button').onClick.listen((e) {
    e.preventDefault();
    exportImportButtons.setAttribute('hidden', '');
    importDialog.removeAttribute('hidden');
  });

  importDir.value = workingDir;

  querySelector('#import-copy-btn').onClick.listen((e) {
    e.preventDefault();

    Future(() {
      importDir.select();
    }).then((_) {
      window.document.execCommand('copy');
    });
  });

  querySelector('#import-dialog-close').onClick.listen((e) {
    e.preventDefault();
    exportImportButtons.removeAttribute('hidden');
    importDialog.setAttribute('hidden', '');
  });
}

String makePrefix(String localPath) {
  var re = RegExp(r'[/\\:]'); // '/', '\' and ':'
  var prefix = localPath.replaceAll(re, '');
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

String makeWorkingDir(String localPath) {
  var i = localPath.lastIndexOf('/');
  var workingDir = localPath.substring('file:///'.length, i + 1);
  if (window.navigator.platform.startsWith('Win')) {
    return workingDir.replaceAll(r'/', r'\');
  }
  return workingDir;
}
