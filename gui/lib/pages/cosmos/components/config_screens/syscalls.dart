import 'package:cosmos_config_controller/data/config_service.dart';
import 'package:cosmos_config_controller/pages/cosmos/components/dropdown_field.dart';
import 'package:cosmos_config_controller/pages/cosmos/components/text_form_field.dart';
import 'package:cosmos_config_controller/utils/config_inherited_widget.dart';
import 'package:cosmos_config_controller/utils/constants.dart';
import 'package:cosmos_config_controller/utils/display_mixin.dart';
import 'package:cosmos_config_controller/utils/toaster_mixin.dart';
import 'package:flutter/material.dart';

class Syscalls extends StatefulWidget {
  static const String title = "Syscalls";

  const Syscalls({Key? key}) : super(key: key);

  @override
  _SyscallsState createState() => _SyscallsState();
}

class _SyscallsState extends State<Syscalls> with DisplayTools, Toaster {
  final _formKey = GlobalKey<FormState>();

  List<TextEditingController> controllers = [];
  Map<String, dynamic> data = {};
  Map<String, bool> visibleWindows = {};
  List<dynamic> syscalls = [];

  void _setData() {
    data = ConfigInheritedWidget.of(context).json;
  }

  TextEditingController _generateController(String initialValue) {
    TextEditingController controller = TextEditingController();
    controller.text = initialValue;
    controllers.add(controller);

    return controller;
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
          width: 95.0,
          child: Wrap(
              alignment: WrapAlignment.spaceBetween,
              children: [Text(key, style: TextStyle(fontSize: 18.0)), wrap]),
        )));
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

  Widget _syscallBuilder(String syscall) {
    List<Widget> children = [];

    // name
    children.add(CustomFormField(
      onChanged: (String value) {
        data['sysCalls']['routed_funcs'][syscall]['name'] = value;
      },
      controller: _generateController(
          data['sysCalls']['routed_funcs'][syscall]['name']),
      label: 'name',
      validator: () {},
    ));
    insertPadding(children);

    // api_header
    children.add(CustomFormField(
      onChanged: (String value) {
        data['sysCalls']['routed_funcs'][syscall]['api_header'] = value;
      },
      controller: _generateController(
          data['sysCalls']['routed_funcs'][syscall]['api_header']),
      label: 'api_header',
      validator: () {},
    ));
    insertPadding(children);

    // sysCall
    children.add(CustomDropDownField(
      value: data['sysCalls']['routed_funcs'][syscall]['sysCall'],
      items: syscalls
          .map((syscall) => DropdownMenuItem(
                value: syscall,
                child: Text(syscall),
              ))
          .toList(),
      label: 'sysCall',
      onChanged: (value) {
        data['sysCalls']['routed_funcs'][syscall]['sysCall'] = value;
        setState(() {});
      },
    ));
    insertPadding(children);

    // user_visible
    children.add(Text('user_visible:'));
    children.add(
      Checkbox(
        value: data['sysCalls']['routed_funcs'][syscall]['user_visible'],
        onChanged: (bool? value) {
          if (value == null) {
            return;
          }
          setState(() {
            data['sysCalls']['routed_funcs'][syscall]['user_visible'] = value;
          });
        },
      ),
    );

    // is_mapped_to_entity
    children.add(Text('is_mapped_to_entity:'));
    children.add(
      Checkbox(
        value: data['sysCalls']['routed_funcs'][syscall]['is_mapped_to_entity'],
        onChanged: (bool? value) {
          if (value == null) {
            return;
          }
          setState(() {
            data['sysCalls']['routed_funcs'][syscall]['is_mapped_to_entity'] =
                value;
          });
        },
      ),
    );
    insertPadding(children);

    // return_type
    children.add(CustomFormField(
      onChanged: (String value) {
        data['sysCalls']['routed_funcs'][syscall]['return_type'] = value;
      },
      controller: _generateController(
          data['sysCalls']['routed_funcs'][syscall]['return_type']),
      label: 'return_type',
      validator: () {},
    ));
    insertPadding(children);

    // args
    children.add(Padding(
      padding: const EdgeInsets.only(bottom: 4.0, top: defaultPadding),
      child: Text('args', style: TextStyle(fontSize: 20.0)),
    ));
    children.add(Container(
      height: 2.0,
      color: bgColor,
    ));

    data['sysCalls']['routed_funcs'][syscall]['args']
        .asMap()
        .forEach((index, arg) {
      int argNumber = index + 1;
      children.add(Padding(
          padding: const EdgeInsets.only(
              left: defaultPadding / 2, top: defaultPadding),
          child: Text("$argNumber. $arg")));
    });

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: children,
    );
  }

  Widget _addArgumentButton(String syscall) {
    return Padding(
      padding: const EdgeInsets.only(
          left: defaultPadding, right: defaultPadding, bottom: defaultPadding),
      child: TextButton(
        onPressed: () {
          showDialog<void>(
              context: context,
              builder: (context) => _addSyscallArgDialog(syscall));
        },
        child: Container(
          width: 60.0,
          height: 25.0,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              Icon(
                Icons.add_rounded,
                size: 18.0,
              ),
              Text("Add"),
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

  String _getNextSystemCallKey() {
    int functionsCount = data['sysCalls']['routed_funcs'].length;

    return "func_$functionsCount";
  }

  Widget _addSyscallButton() {
    return Padding(
      padding: const EdgeInsets.only(
          right: defaultPadding,
          bottom: defaultPadding,
          top: defaultPadding / 2),
      child: TextButton(
        onPressed: () {
          Map<String, dynamic> newSyscall = {
            "name": "",
            "api_header": "",
            "sysCall": null,
            "user_visible": false,
            "is_mapped_to_entity": false,
            "args": [],
            "return_type": ""
          };

          String nextSystemCallKey = _getNextSystemCallKey();
          data['sysCalls']['routed_funcs'][nextSystemCallKey] = newSyscall;
          displayMessage(
              context, "New routed_funcs `$nextSystemCallKey` was added.");
          setState(() {});
        },
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
              Text("Add Function"),
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

  Widget _syscallsBuilder() {
    List<Widget> children = [];
    _setData();

    data['sysCalls']['routed_funcs'].forEach((key, val) {
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
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.start,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(defaultPadding),
                      child: _syscallBuilder(key),
                    ),
                    _addArgumentButton(key)
                  ],
                )),
          ),
        );
        insertPadding(children, height: 30.0);
      }
    });

    children.add(_addSyscallButton());

    return Padding(
      padding: const EdgeInsets.only(left: 8.0),
      child: Form(
        key: _formKey,
        child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: children),
      ),
    );
  }

  AlertDialog _addSyscallArgDialog(String syscall) {
    TextEditingController controller = TextEditingController();

    return AlertDialog(
      backgroundColor: secondaryColor,
      title: Text(syscall),
      contentPadding: EdgeInsets.zero,
      content: Container(
        width: 400.0,
        height: 140.0,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Padding(
              padding: const EdgeInsets.only(
                  left: 30.0, bottom: 30.0, right: 30.0, top: 20.0),
              child: CustomFormField(
                onChanged: (val) {},
                label: 'arg',
                controller: controller,
                validator: () {},
              ),
            )
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () {
            Navigator.pop(context);
          },
          child: Text('Cancel'),
          style: ButtonStyle(
            backgroundColor: MaterialStateProperty.all<Color>(tertiaryColor),
            foregroundColor: MaterialStateProperty.all<Color>(Colors.white),
          ),
        ),
        TextButton(
          onPressed: () {
            String newArg = controller.text;

            if (newArg.isEmpty) {
              displayErrorMessage(
                  context, "New argument wasn't added. Input field was empty.");
              Navigator.pop(context);
              return;
            }

            data['sysCalls']['routed_funcs'][syscall]['args'].add(newArg);

            setState(() {});
            displayMessage(context,
                "New argument `$newArg` for routed_func `$syscall` was added.");
            Navigator.pop(context);
          },
          child: Text('Save'),
          style: ButtonStyle(
            backgroundColor: MaterialStateProperty.all<Color>(tertiaryColor),
            foregroundColor: MaterialStateProperty.all<Color>(Colors.white),
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<dynamic>(
      future: ConfigService.instance.readJson(context, ConfigFile.SystemCalls),
      builder: (BuildContext context, AsyncSnapshot<dynamic> snapshot) {
        if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        } else if (snapshot.hasData) {
          syscalls = snapshot.data;
          return _syscallsBuilder();
        } else {
          return Center(child: Text('Loading...'));
        }
      },
    );
  }
}
