void main() {
  var s = r'file:///D:/ComputerScience/JavaScript/my-projects/small-plans/dart_plans/'
      r'build/你好/index.html';
  var exp = RegExp(r'[\/\\:]');
  var matches = exp.allMatches(s);
  print(matches.map((m) => m.group(0)));
  s = s.replaceAll(exp, '');
  print(s);

  var numbers = RegExp(r'[ea]');
  var someDigits = r'llamas live 15 to 20 years'
                   r'abcdefghijk';
  matches = numbers.allMatches(someDigits);
  print(matches.map((m) => m.group(0)));
  someDigits = someDigits.replaceAll(numbers, '');
  print(someDigits);
}
