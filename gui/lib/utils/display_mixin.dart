import 'dart:math';

import 'package:cosmos_config_controller/models/custom_element.dart';
import 'package:cosmos_config_controller/utils/constants.dart';
import 'package:flutter/material.dart';

mixin DisplayTools {
  void insertPadding(List<Widget> children, {double height = defaultPadding}) {
    children.add(SizedBox(height: defaultPadding));
  }

  void insertSeparator(List<Widget> children) {
    children.add(Padding(
      padding: const EdgeInsets.only(bottom: 12.0, top: 10.0),
      child: Container(height: 2.0, color: bgColor),
    ));
  }

  List<DropdownMenuItem> generateDropDownItems(data) {
    List<DropdownMenuItem> items = [];
    int i = 0;
    data.forEach((index, value) {
      items.add(DropdownMenuItem(
        value: i,
        child: Text(value['name']),
      ));
      i += 1;
    });

    return items;
  }

  List<DropdownMenuItem> generateTaskItems(data, elType) {
    List<DropdownMenuItem> items = [];

    data['cores'].forEach((core, valueVal) {
      valueVal['programs'].forEach((program, programVal) => {
            programVal[elType].forEach((task, taskVal) {
              var id = task.split('_');
              var coreID = core.split('_');
              var programID = program.split('_');

              CustomElement taskObj = CustomElement(
                  id: int.parse(id.last),
                  coreID: int.parse(coreID.last),
                  programID: int.parse(programID.last),
                  name: taskVal['name']);

              items.add(DropdownMenuItem(
                value: taskObj,
                child: Text(taskObj.name),
              ));
            })
          });
    });

    return items;
  }

  List<DropdownMenuItem> generatePowerOfTwoItems() {
    List<DropdownMenuItem> items = [];
    for (var i = 5; i <= 20; i++) {
      num val = pow(2, i);
      items.add(DropdownMenuItem(
        value: val,
        child: Text(_numberShortCut(val.toString())),
      ));
    }

    return items;
  }

  String _numberShortCut(String number) {
    String shortNumber = "${number}B";

    switch (number.length) {
      case 9:
        shortNumber = "${number.substring(0, 3)}MB";
        break;
      case 8:
        shortNumber = "${number.substring(0, 2)}MB";
        break;
      case 7:
        shortNumber = "${number.substring(0, 1)}MB";
        break;
      case 6:
        shortNumber = "${number.substring(0, 3)}kB";
        break;
      case 5:
        shortNumber = "${number.substring(0, 2)}kB";
        break;
      case 4:
        shortNumber = "${number.substring(0, 1)}kB";
        break;

      default:
        break;
    }

    return shortNumber;
  }
}
