import 'package:cosmos_config_controller/utils/config_inherited_widget.dart';
import 'package:cosmos_config_controller/utils/constants.dart';
import 'package:cosmos_config_controller/utils/toaster_mixin.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class Switches extends StatefulWidget {
  static const String title = "Switches";

  Switches({Key? key}) : super(key: key);

  @override
  _SwitchesState createState() => _SwitchesState();
}

class _SwitchesState extends State<Switches> with Toaster {
  Map<String, dynamic> data = {};
  bool initialSwitchVal = false;

  void _setData() {
    data = ConfigInheritedWidget.of(context).json;
  }

  Widget _switchesBuilder() {
    List<Widget> children = [];
    _setData();

    children.add(Container(
      color: secondaryColor,
    ));

    data['switches'].forEach((key, val) {
      children.add(Text("$key:"));
      children.add(
        Checkbox(
          value: data['switches'][key],
          onChanged: (bool? value) {
            if (value == null) {
              return;
            }
            setState(() {
              data['switches'][key] = value;
            });
          },
        ),
      );
    });

    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Flexible(
          fit: FlexFit.loose,
          flex: 6,
          child: Container(
              decoration: BoxDecoration(
                  color: secondaryColor,
                  borderRadius: BorderRadius.all(Radius.circular(10.0))),
              width: 500,
              child: Padding(
                padding: const EdgeInsets.all(defaultPadding),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: children,
                ),
              )),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return _switchesBuilder();
  }
}
