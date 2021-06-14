import 'package:flutter/widgets.dart';

class ConfigInheritedWidget extends InheritedWidget {
  final Map<String, dynamic> json;

  ConfigInheritedWidget(Widget child, this.json) : super(child: child);

  @override
  bool updateShouldNotify(ConfigInheritedWidget old) => old.json != json;

  static ConfigInheritedWidget of(BuildContext context) =>
      context.dependOnInheritedWidgetOfExactType<ConfigInheritedWidget>()!;
}
