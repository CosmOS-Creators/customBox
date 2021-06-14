import 'package:cosmos_config_controller/models/custom_element.dart';
import 'package:cosmos_config_controller/pages/cosmos/components/dropdown_field.dart';
import 'package:cosmos_config_controller/pages/cosmos/components/text_form_field.dart';
import 'package:cosmos_config_controller/utils/config_inherited_widget.dart';
import 'package:cosmos_config_controller/utils/constants.dart';
import 'package:cosmos_config_controller/utils/display_mixin.dart';
import 'package:cosmos_config_controller/utils/toaster_mixin.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';

enum BufferElement {
  TasksReadPermissions,
  TasksWritePermissions,
  ThreadsReadPermissions,
  ThreadsWritePermissions
}

// TODO: collect all task/thread
// TODO: get selected task/thread in DD

extension BufferElementEx on BufferElement {
  String? getType() {
    String element = this.toString().split('.').last;
    return "${element[0].toLowerCase()}${element.substring(1)}";
  }
}

class Buffers extends StatefulWidget {
  static const String title = "Buffers";

  const Buffers({Key? key}) : super(key: key);

  @override
  _BuffersState createState() => _BuffersState();
}

class _BuffersState extends State<Buffers> with DisplayTools, Toaster {
  final _formKey = GlobalKey<FormState>();

  Map<String, dynamic> data = {};

  List<TextEditingController> controllers = [];

  Map<String, bool> visibleWindows = {};

  List<DropdownMenuItem> taskItems = [];
  List<DropdownMenuItem> threadItems = [];
  Map<String, CustomElement?> _selectedItems = {};

  String currentText = "";
  List<String> _suggestions = [];
  List<String> added = [];

  void _setData() {
    data = ConfigInheritedWidget.of(context).json;

    taskItems = generateTaskItems(data, 'tasks');
    threadItems = generateTaskItems(data, 'threads');

    _findSuggestions();
  }

  void _findSuggestions() {
    Map<String, int> buffers = {};

    for (var buffer in data['buffers'].values) {
      if (!buffer['isDoubleBuffer']) {
        continue;
      }

      if (!buffers.containsKey(buffer['double']['name'])) {
        buffers[buffer['double']['name']] = 1;
      } else {
        buffers[buffer['double']['name']] =
            buffers[buffer['double']['name']]! + 1;
      }
    }

    buffers.forEach((key, value) {
      if (value == 1 && !_suggestions.contains(key)) {
        _suggestions.add(key);
      }
    });

    print(_suggestions);
  }

  TextEditingController _generateController(String initialValue) {
    TextEditingController controller = TextEditingController();
    controller.text = initialValue;
    controllers.add(controller);

    return controller;
  }

  void _onWindowTap(String key) {
    if (!visibleWindows.containsKey(key)) {
      visibleWindows[key] = true;
    } else if (!visibleWindows[key]!) {
      visibleWindows[key] = true;
    } else {
      visibleWindows[key] = false;
    }
    setState(() {});
  }

  void _arrowDropDown(List<Widget> children, String key) {
    Widget wrap;

    if (visibleWindows[key] != null && visibleWindows[key]!) {
      wrap = Padding(
        padding: const EdgeInsets.only(left: 8.0, top: 6.0),
        child: Icon(
          Icons.arrow_circle_up_sharp,
          color: Colors.white,
          size: 18.0,
        ),
      );
    } else {
      wrap = Padding(
        padding: const EdgeInsets.only(left: 8.0, top: 6.0),
        child: Icon(
          Icons.arrow_circle_down_sharp,
          color: Colors.white,
          size: 18.0,
        ),
      );
    }

    children.add(GestureDetector(
        onTap: () {
          _onWindowTap(key);
        },
        child: Container(
          width: 110.0,
          child: Wrap(
              alignment: WrapAlignment.spaceBetween,
              children: [Text(key, style: TextStyle(fontSize: 18.0)), wrap]),
        )));
  }

  String? _getNextElementKey(String buffer, BufferElement element) {
    int? nextElementNum;

    switch (element) {
      case BufferElement.TasksReadPermissions:
        nextElementNum = data['buffers'][buffer]['tasksReadPermissions'].length;
        break;
      case BufferElement.TasksWritePermissions:
        nextElementNum =
            data['buffers'][buffer]['tasksWritePermissions'].length;
        break;
      case BufferElement.ThreadsReadPermissions:
        nextElementNum =
            data['buffers'][buffer]['threadsReadPermissions'].length;
        break;
      case BufferElement.ThreadsWritePermissions:
        nextElementNum =
            data['buffers'][buffer]['threadsWritePermissions'].length;
        break;

      default:
    }

    return "element_${nextElementNum!.toString()}";
  }

  void _onElementAdd(String buffer, BufferElement element) {
    String elementTypeKey = element.getType()!;
    String nextElementKey = _getNextElementKey(buffer, element)!;

    Map<String, dynamic> newElement = {"core": "-1", "program": "-1"};

    if (element == BufferElement.TasksReadPermissions ||
        element == BufferElement.TasksWritePermissions) {
      newElement["task"] = "-1";
    } else if (element == BufferElement.ThreadsReadPermissions ||
        element == BufferElement.ThreadsWritePermissions) {
      newElement["thread"] = "-1";
    }

    data['buffers'][buffer][elementTypeKey][nextElementKey] = newElement;
    displayMessage(context, "New element `$nextElementKey` was added.");
    setState(() {});
  }

  CustomElement? _getSelectedItem(elements, elementData, type) {
    CustomElement? task;
    for (var element in elements) {
      if (element.value.id.toString() == elementData[type] &&
          element.value.programID.toString() == elementData['program'] &&
          element.value.coreID.toString() == elementData['core']) {
        task = element.value;
      }
    }

    return task;
  }

  Widget _addElementButton(String buffer, BufferElement element) {
    return Padding(
      padding: const EdgeInsets.only(
          right: defaultPadding, bottom: defaultPadding, top: defaultPadding),
      child: TextButton(
        onPressed: () => _onElementAdd(buffer, element),
        child: Container(
          width: 120.0,
          height: 25.0,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              Icon(
                Icons.add_rounded,
                size: 18.0,
              ),
              Text("Add Element"),
            ],
          ),
        ),
        style: ButtonStyle(
          backgroundColor: MaterialStateProperty.all<Color>(tertiaryColor),
          foregroundColor: MaterialStateProperty.all<Color>(Colors.white),
        ),
      ),
    );
  }

  void _onElementChange(String buffer, String element, String permissionType,
      CustomElement value) {
    data['buffers'][buffer][permissionType][element]['task'] =
        value.id.toString();
    data['buffers'][buffer][permissionType][element]['program'] =
        value.programID.toString();
    data['buffers'][buffer][permissionType][element]['core'] =
        value.coreID.toString();

    setState(() {});
  }

  String _getNextBufferKey() {
    int functionsCount = data['buffers'].length;

    return "buffer_$functionsCount";
  }

  void _onBufferAdd() {
    Map<String, dynamic> newBuffer = {
      "name": "",
      "size": null,
      "isDoubleBuffer": false,
      "double": {"name": ""},
      "tasksReadPermissions": {},
      "tasksWritePermissions": {},
      "threadsReadPermissions": {},
      "threadsWritePermissions": {}
    };

    final String nextBufferKey = _getNextBufferKey();
    data['buffers'][nextBufferKey] = newBuffer;
    displayMessage(context, "New buffer `$nextBufferKey` was added.");
    setState(() {});
  }

  Widget _addBufferButton() {
    return Padding(
      padding: const EdgeInsets.only(
          right: defaultPadding,
          bottom: defaultPadding,
          top: defaultPadding / 2),
      child: TextButton(
        onPressed: _onBufferAdd,
        child: Container(
          width: 100.0,
          height: 25.0,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              Icon(
                Icons.add_rounded,
                size: 18.0,
              ),
              Text("Add Buffer"),
            ],
          ),
        ),
        style: ButtonStyle(
          backgroundColor: MaterialStateProperty.all<Color>(tertiaryColor),
          foregroundColor: MaterialStateProperty.all<Color>(Colors.white),
        ),
      ),
    );
  }

  Widget _bufferBuilder(String buffer) {
    List<Widget> children = [];

    // name
    children.add(CustomFormField(
      onChanged: (String value) {
        data['buffers'][buffer]['name'] = value;
      },
      controller: _generateController(data['buffers'][buffer]['name']),
      label: 'name',
      validator: () {},
    ));
    children.add(SizedBox(height: defaultPadding));

    // size
    children.add(CustomDropDownField(
      value: data['buffers'][buffer]['size'] != null
          ? int.parse(data['buffers'][buffer]['size'])
          : null,
      items: generatePowerOfTwoItems(),
      label: 'size',
      onChanged: (value) {
        data['buffers'][buffer]['size'] = value.toString();
        setState(() {});
      },
    ));
    insertPadding(children);

    // isDoubleBuffer
    children.add(Text('isDoubleBuffer:'));
    children.add(
      Checkbox(
        value: data['buffers'][buffer]['isDoubleBuffer'],
        onChanged: (bool? value) {
          if (value == null) {
            return;
          }
          if (!value) {
            data['buffers'][buffer]['double']['name'] = '';
          }

          setState(() {
            data['buffers'][buffer]['isDoubleBuffer'] = value;
          });
        },
      ),
    );

    if (data['buffers'][buffer]['isDoubleBuffer']) {
      // double
      children.add(Padding(
        padding: const EdgeInsets.only(bottom: 4.0, top: defaultPadding),
        child: Text('double', style: TextStyle(fontSize: 20.0)),
      ));

      insertSeparator(children);

      final TextEditingController _typeAheadController = TextEditingController(
          text: data['buffers'][buffer]['double']['name']);

      children.add(TypeAheadFormField(
        textFieldConfiguration: TextFieldConfiguration(
            onChanged: (value) =>
                data['buffers'][buffer]['double']['name'] = value,
            controller: _typeAheadController,
            cursorColor: Colors.white10,
            decoration: InputDecoration(
              enabledBorder: const OutlineInputBorder(
                borderSide: const BorderSide(color: Colors.white, width: 0.0),
              ),
              focusedBorder: const OutlineInputBorder(
                borderSide: const BorderSide(color: Colors.grey, width: 0.0),
              ),
              labelText: 'name',
              labelStyle: TextStyle(fontSize: 17.0, color: Colors.white60),
              border: OutlineInputBorder(),
            )),
        suggestionsCallback: (pattern) {
          return _suggestions;
        },
        itemBuilder: (context, suggestion) {
          return ListTile(
            title: Text(suggestion.toString()),
          );
        },
        transitionBuilder: (context, suggestionsBox, controller) {
          return suggestionsBox;
        },
        onSuggestionSelected: (suggestion) {
          _typeAheadController.text = suggestion.toString();
        },
        hideOnEmpty: true,
        onSaved: (value) => data['buffers'][buffer]['double']['name'] = value,
      ));

      // children.add(CustomFormField(
      //   onChanged: (String value) {
      //     data['buffers'][buffer]['double']['name'] = value;
      //   },
      //   controller:
      //       _generateController(data['buffers'][buffer]['double']['name']),
      //   label: 'name',
      //   validator: () {},
      // ));
    }

    // tasksReadPermissions
    children.add(Padding(
      padding: const EdgeInsets.only(bottom: 4.0, top: defaultPadding),
      child: Text('tasksReadPermissions', style: TextStyle(fontSize: 20.0)),
    ));
    children.add(Container(
      height: 2.0,
      color: bgColor,
    ));

    // elements
    data['buffers'][buffer]['tasksReadPermissions'].forEach((element, val) {
      insertPadding(children);

      _selectedItems[element] = _getSelectedItem(taskItems,
          data['buffers'][buffer]['tasksReadPermissions'][element], 'task');

      children.add(CustomDropDownField(
          value: _selectedItems[element],
          items: taskItems,
          label: 'task',
          onChanged: (value) => _onElementChange(
              buffer, element, 'tasksReadPermissions', value)));
    });

    children.add(_addElementButton(buffer, BufferElement.TasksReadPermissions));

    // tasksWritePermissions
    children.add(Padding(
      padding: const EdgeInsets.only(bottom: 4.0, top: defaultPadding),
      child: Text('tasksWritePermissions', style: TextStyle(fontSize: 20.0)),
    ));
    children.add(Container(
      height: 2.0,
      color: bgColor,
    ));

    // elements
    data['buffers'][buffer]['tasksWritePermissions'].forEach((element, val) {
      insertPadding(children);

      _selectedItems[element] = _getSelectedItem(taskItems,
          data['buffers'][buffer]['tasksWritePermissions'][element], 'task');

      // element fields
      children.add(CustomDropDownField(
          value: _selectedItems[element],
          items: taskItems,
          label: 'task',
          onChanged: (value) => _onElementChange(
              buffer, element, 'tasksWritePermissions', value)));
    });

    children
        .add(_addElementButton(buffer, BufferElement.TasksWritePermissions));

    // threadsReadPermissions
    children.add(Padding(
      padding: const EdgeInsets.only(bottom: 4.0, top: defaultPadding),
      child: Text('threadsReadPermissions', style: TextStyle(fontSize: 20.0)),
    ));
    children.add(Container(
      height: 2.0,
      color: bgColor,
    ));

    // elements
    data['buffers'][buffer]['threadsReadPermissions'].forEach((element, val) {
      _selectedItems[element] = _getSelectedItem(threadItems,
          data['buffers'][buffer]['threadsReadPermissions'][element], 'thread');

      insertPadding(children);

      // element fields
      children.add(CustomDropDownField(
          value: _selectedItems[element],
          items: threadItems,
          label: 'thread',
          onChanged: (value) => _onElementChange(
              buffer, element, 'threadsReadPermissions', value)));
    });

    children
        .add(_addElementButton(buffer, BufferElement.ThreadsReadPermissions));

    // threadsWritePermissions
    children.add(Padding(
      padding: const EdgeInsets.only(bottom: 4.0, top: defaultPadding),
      child: Text('threadsWritePermissions', style: TextStyle(fontSize: 20.0)),
    ));
    children.add(Container(
      height: 2.0,
      color: bgColor,
    ));

    // elements
    data['buffers'][buffer]['threadsWritePermissions'].forEach((element, val) {
      _selectedItems[element] = _getSelectedItem(
          threadItems,
          data['buffers'][buffer]['threadsWritePermissions'][element],
          'thread');

      insertPadding(children);

      // element fields
      children.add(CustomDropDownField(
          value: _selectedItems[element],
          items: threadItems,
          label: 'thread',
          onChanged: (value) => _onElementChange(
              buffer, element, 'threadsWritePermissions', value)));
    });

    children
        .add(_addElementButton(buffer, BufferElement.ThreadsWritePermissions));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: children,
    );
  }

  Widget _buffersBuilder() {
    List<Widget> children = [];
    _setData();

    data['buffers'].forEach((key, val) {
      _arrowDropDown(children, key);

      if (visibleWindows[key] != null && visibleWindows[key]!) {
        children.add(
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
                  child: _bufferBuilder(key),
                )),
          ),
        );
        insertPadding(children, height: 30.0);
      }
    });

    children.add(_addBufferButton());

    return Form(
      key: _formKey,
      child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: children),
    );
  }

  @override
  Widget build(BuildContext context) {
    return _buffersBuilder();
  }
}
