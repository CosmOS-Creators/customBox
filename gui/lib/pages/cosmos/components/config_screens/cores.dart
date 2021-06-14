import 'package:cosmos_config_controller/data/config_service.dart';
import 'package:cosmos_config_controller/pages/cosmos/components/dropdown_field.dart';
import 'package:cosmos_config_controller/pages/cosmos/components/text_form_field.dart';
import 'package:cosmos_config_controller/utils/config_inherited_widget.dart';
import 'package:cosmos_config_controller/utils/constants.dart';
import 'package:cosmos_config_controller/utils/display_mixin.dart';
import 'package:cosmos_config_controller/utils/toaster_mixin.dart';
import 'package:flutter/material.dart';

enum CoreDetailTab { Programs, Scheduler, SystemJobs, Unmapped }

class Cores extends StatefulWidget {
  static const String title = "Cores";

  const Cores({Key? key}) : super(key: key);

  @override
  _CoresState createState() => _CoresState();
}

class _CoresState extends State<Cores> with DisplayTools, Toaster {
  final _formKey = GlobalKey<FormState>();

  Map<String, dynamic> data = {};

  Map<String, dynamic> mcuData = {};
  List<String> memoryTypes = [];

  List<dynamic> sysJobsData = [];

  List<TextEditingController> controllers = [];
  Map<String, bool> visibleWindows = {};
  CoreDetailTab _coreDetailTab = CoreDetailTab.Programs;

  void _setData() {
    data = ConfigInheritedWidget.of(context).json;
    _collectMemoryTypes();
  }

  void _collectMemoryTypes() {
    mcuData['memory'].forEach((key, memory) {
      String item = memory['name'];

      if (!memoryTypes.contains(item)) {
        memoryTypes.add(memory['name']);
      }
    });
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

  void _unselectBootUpCores() {
    for (var core in data['cores'].values) {
      core['bootOs'] = false;
    }
  }

  void _arrowDropDown(List<Widget> children, String key,
      {space: 90.0, fontSize: 15.0}) {
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
          width: space,
          child: Wrap(alignment: WrapAlignment.spaceBetween, children: [
            Text(key,
                style: TextStyle(fontSize: fontSize, color: Colors.white70)),
            wrap
          ]),
        )));
  }

  void _tasksBuilder(List<Widget> children, String core, String program) {
    // tasks
    children.add(Padding(
      padding: const EdgeInsets.only(bottom: 4.0, top: 10.0),
      child: Text('tasks:', style: TextStyle(fontSize: 17.0)),
    ));

    data['cores'][core]['programs'][program]['tasks']
        .forEach((keyTask, valKey) {
      _taskBuilder(children, core, program, keyTask);
    });

    children.add(_addTaskButton(core, program));
  }

  void _taskBuilder(
      List<Widget> children, String core, String program, String task) {
    _arrowDropDown(children, task);

    if (visibleWindows[task] != null && visibleWindows[task]!) {
      insertPadding(children);
      // name
      children.add(CustomFormField(
        onChanged: (String value) {
          data['cores'][core]['programs'][program]['tasks'][task]['name'] =
              value;
        },
        controller: _generateController(
            data['cores'][core]['programs'][program]['tasks'][task]['name']),
        label: 'name',
        validator: () {},
      ));
      insertPadding(children);

      children.add(Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // wcet
          Container(
            width: 270.0,
            child: CustomFormField(
              onChanged: (String value) {
                data['cores'][core]['programs'][program]['tasks'][task]
                    ['wcet'] = value;
              },
              controller: _generateController(data['cores'][core]['programs']
                  [program]['tasks'][task]['wcet']),
              label: 'wcet',
              validator: () {},
            ),
          ),

          // period
          Container(
            width: 270.0,
            child: CustomFormField(
              onChanged: (String value) {
                data['cores'][core]['programs'][program]['tasks'][task]
                    ['period'] = value;
              },
              controller: _generateController(data['cores'][core]['programs']
                  [program]['tasks'][task]['period']),
              label: 'period',
              validator: () {},
            ),
          ),
        ],
      ));

      insertPadding(children);

      // floatingPoint
      children.add(Text('floatingPoint:'));
      children.add(
        Checkbox(
          value: data['cores'][core]['programs'][program]['tasks'][task]
              ['floatingPoint'],
          onChanged: (bool? value) {
            if (value == null) {
              return;
            }
            setState(() {
              data['cores'][core]['programs'][program]['tasks'][task]
                  ['floatingPoint'] = value;
            });
          },
        ),
      );

      insertPadding(children);

      // size
      children.add(CustomDropDownField(
        value: data['cores'][core]['programs'][program]['tasks'][task]['stack']
                    ['size'] !=
                null
            ? int.parse(data['cores'][core]['programs'][program]['tasks'][task]
                ['stack']['size'])
            : null,
        items: generatePowerOfTwoItems(),
        label: 'stack size',
        onChanged: (value) {
          data['cores'][core]['programs'][program]['tasks'][task]['stack']
              ['size'] = value.toString();
          setState(() {});
        },
      ));

      insertPadding(children);
    }
  }

  void _threadsBuilder(List<Widget> children, String core, String program) {
    // threads
    children.add(Padding(
      padding: const EdgeInsets.only(bottom: 4.0, top: 10.0),
      child: Text('threads:', style: TextStyle(fontSize: 17.0)),
    ));

    data['cores'][core]['programs'][program]['threads']
        .forEach((keyThread, valThread) {
      _threadBuilder(children, core, program, keyThread);
    });

    children.add(_addThreadButton(core, program));

    insertPadding(children);
  }

  void _threadBuilder(
      List<Widget> children, String core, String program, String thread) {
    _arrowDropDown(children, thread, space: 110.0);

    if (visibleWindows[thread] != null && visibleWindows[thread]!) {
      insertPadding(children);

      // name
      children.add(CustomFormField(
        onChanged: (String value) {
          data['cores'][core]['programs'][program]['threads'][thread]['name'] =
              value;
        },
        controller: _generateController(data['cores'][core]['programs'][program]
            ['threads'][thread]['name']),
        label: 'name',
        validator: () {},
      ));
      insertPadding(children);

      // floatingPoint
      children.add(Text('floatingPoint:'));
      children.add(
        Checkbox(
          value: data['cores'][core]['programs'][program]['threads'][thread]
              ['floatingPoint'],
          onChanged: (bool? value) {
            if (value == null) {
              return;
            }
            setState(() {
              data['cores'][core]['programs'][program]['threads'][thread]
                  ['floatingPoint'] = value;
            });
          },
        ),
      );

      insertPadding(children);

      // size
      children.add(CustomDropDownField(
        value: data['cores'][core]['programs'][program]['threads'][thread]
                    ['stack']['size'] !=
                null
            ? int.parse(data['cores'][core]['programs'][program]['threads']
                [thread]['stack']['size'])
            : null,
        items: generatePowerOfTwoItems(),
        label: 'stack size',
        onChanged: (value) {
          data['cores'][core]['programs'][program]['threads'][thread]['stack']
              ['size'] = value.toString();
          setState(() {});
        },
      ));

      insertPadding(children);
    }
  }

  String _getNextProgramKey(String core) {
    int functionsCount = data['cores'][core]['programs'].length;

    return "program_$functionsCount";
  }

  void _onProgramAdd(String core) {
    final Map<String, dynamic> newProgram = {
      "name": "",
      "size": null,
      "memory": null,
      "tasks": {},
      "threads": {}
    };

    final String nextProgramKey = _getNextProgramKey(core);
    data['cores'][core]['programs'][nextProgramKey] = newProgram;
    displayMessage(context, "New core `$nextProgramKey` was added.");
    setState(() {});
  }

  Widget _addProgramButton(String core) {
    return Padding(
      padding: const EdgeInsets.only(
          right: defaultPadding,
          bottom: defaultPadding,
          top: defaultPadding / 2),
      child: TextButton(
        onPressed: () => _onProgramAdd(core),
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
              Text("Add Program"),
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

  String _getNextGroupKey(String core) {
    int functionsCount = data['cores'][core]['sysJobs']['groups'].length;

    return "group_$functionsCount";
  }

  void _onGroupAdd(String core) {
    final Map<String, dynamic> newProgram = {
      "tickMultiplicator": "",
      "handlers": [],
      "api_headers": []
    };

    final String nextGroupKey = _getNextGroupKey(core);
    data['cores'][core]['sysJobs']['groups'][nextGroupKey] = newProgram;
    displayMessage(context, "New group `$nextGroupKey` was added.");
    setState(() {});
  }

  Widget _addGroupButton(String core) {
    return Padding(
      padding: const EdgeInsets.only(
          right: defaultPadding,
          bottom: defaultPadding,
          top: defaultPadding / 2),
      child: TextButton(
        onPressed: () => _onGroupAdd(core),
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
              Text("Add Group"),
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

  String _getNextTaskKey(String core, String program) {
    int functionsCount =
        data['cores'][core]['programs'][program]['tasks'].length;

    return "task_$functionsCount";
  }

  void _onTaskAdd(String core, String program) {
    final Map<String, dynamic> newTask = {
      "name": "",
      "wcet": "",
      "period": "",
      "floatingPoint": false,
      "isIdle": false,
      "isSysJob": false,
      "stack": {"size": null}
    };

    final String nextTaskKey = _getNextTaskKey(core, program);
    data['cores'][core]['programs'][program]['tasks'][nextTaskKey] = newTask;
    displayMessage(context, "New task `$nextTaskKey` was added.");
    setState(() {});
  }

  Widget _addTaskButton(String core, String program) {
    return Padding(
      padding: const EdgeInsets.only(
          right: defaultPadding,
          bottom: defaultPadding,
          top: defaultPadding / 2),
      child: TextButton(
        onPressed: () => _onTaskAdd(core, program),
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
              Text("Add Task"),
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

  String _getNextThreadKey(String core, String program) {
    int functionsCount =
        data['cores'][core]['programs'][program]['threads'].length;

    return "thread_$functionsCount";
  }

  void _onThreadAdd(String core, String program) {
    final Map<String, dynamic> newThread = {
      "name": "",
      "floatingPoint": false,
      "isIdle": false,
      "stack": {"size": null}
    };

    final String nextThreadKey = _getNextThreadKey(core, program);
    data['cores'][core]['programs'][program]['threads'][nextThreadKey] =
        newThread;
    displayMessage(context, "New thread `$nextThreadKey` was added.");
    setState(() {});
  }

  Widget _addThreadButton(String core, String program) {
    return Padding(
      padding: const EdgeInsets.only(
          right: defaultPadding,
          bottom: defaultPadding,
          top: defaultPadding / 2),
      child: TextButton(
        onPressed: () => _onThreadAdd(core, program),
        child: Container(
          width: 110.0,
          height: 25.0,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              Icon(
                Icons.add_rounded,
                size: 18.0,
              ),
              Text("Add Thread"),
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

  Widget _addHandlerButton(String core, String group) {
    return Padding(
      padding: const EdgeInsets.only(
          right: defaultPadding,
          bottom: defaultPadding,
          top: defaultPadding / 2),
      child: TextButton(
        onPressed: () {
          showDialog<void>(
              context: context,
              builder: (context) => _addHandlerDialog(core, group));
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

  Widget _addAPIHeaderButton(String core, String group) {
    return Padding(
      padding: const EdgeInsets.only(
          right: defaultPadding,
          bottom: defaultPadding,
          top: defaultPadding / 2),
      child: TextButton(
        onPressed: () {
          showDialog<void>(
              context: context,
              builder: (context) => _addAPIHeaderDialog(core, group));
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

  AlertDialog _addAPIHeaderDialog(String core, String group) {
    TextEditingController controller = TextEditingController();

    return AlertDialog(
      backgroundColor: secondaryColor,
      title: Text(core),
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
                label: 'api header',
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
            String newAPIHeader = controller.text;

            if (newAPIHeader.isEmpty) {
              displayErrorMessage(context,
                  "New API header wasn't added. Input field was empty.");
              Navigator.pop(context);
              return;
            }

            data['cores'][core]['sysJobs']['groups'][group]['api_headers']
                .add(newAPIHeader);

            setState(() {});
            displayMessage(
                context, "New API header `$newAPIHeader` was added.");
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

  AlertDialog _addHandlerDialog(String core, String group) {
    TextEditingController controller =
        TextEditingController(text: sysJobsData.first);

    return AlertDialog(
      backgroundColor: secondaryColor,
      title: Text(group),
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
              child: CustomDropDownField(
                value: controller.text,
                items: sysJobsData
                    .map((item) => DropdownMenuItem(
                          child: Text(item),
                          value: item,
                        ))
                    .toList(),
                label: 'handler',
                onChanged: (value) {
                  controller.text = value.toString();
                  setState(() {});
                },
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
            String newHandler = controller.text;

            if (newHandler.isEmpty) {
              displayErrorMessage(
                  context, "New argument wasn't added. Input field was empty.");
              Navigator.pop(context);
              return;
            }

            data['cores'][core]['sysJobs']['groups'][group]['handlers']
                .add(newHandler);

            setState(() {});
            displayMessage(context, "New handler `$newHandler` was added.");
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

  void _programsBuilder(List<Widget> children, String core) {
    // programs
    data['cores'][core]['programs'].forEach((program, val) {
      _programBuilder(children, core, program);
    });

    children.add(_addProgramButton(core));
  }

  void _programBuilder(List<Widget> children, String core, String program) {
    _arrowDropDown(children, program, space: 130.0, fontSize: 18.0);

    if (visibleWindows[program] != null && visibleWindows[program]!) {
      insertPadding(children);

      // name
      children.add(CustomFormField(
        onChanged: (String value) {
          data['cores'][core]['programs'][program]['name'] = value;
        },
        controller: _generateController(
            data['cores'][core]['programs'][program]['name']),
        label: 'name',
        validator: () {},
      ));
      insertPadding(children);

      children.add(
          Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
        // size
        Container(
          width: 270.0,
          child: CustomDropDownField(
            value: data['cores'][core]['programs'][program]['size'] != null
                ? int.parse(data['cores'][core]['programs'][program]['size'])
                : null,
            items: generatePowerOfTwoItems(),
            label: 'size',
            onChanged: (value) {
              data['cores'][core]['programs'][program]['size'] =
                  value.toString();
              setState(() {});
            },
          ),
        ),

        Container(
          width: 270.0,
          child: CustomDropDownField(
              value: data['cores'][core]['programs'][program]['memory'],
              items: memoryTypes
                  .map((item) => DropdownMenuItem(
                        child: Text(item),
                        value: item,
                      ))
                  .toList(),
              label: 'memory',
              onChanged: (value) {
                data['cores'][core]['programs'][program]['memory'] = value;
              }),
        )
      ]));

      insertPadding(children);

      _tasksBuilder(children, core, program);
      _threadsBuilder(children, core, program);
    }
  }

  void _schedulerBuilder(List<Widget> children, String core) {
    // hyperTick
    children.add(CustomFormField(
      onChanged: (String value) {
        data['cores'][core]['scheduler']['hyperTick'] = value;
      },
      controller:
          _generateController(data['cores'][core]['scheduler']['hyperTick']),
      label: 'hyperTick',
      validator: () {},
    ));
    insertPadding(children);

    // sync
    children.add(Text('sync:'));
    children.add(
      Checkbox(
        value: data['cores'][core]['scheduler']['sync'],
        onChanged: (bool? value) {
          if (value == null) {
            return;
          }
          setState(() {
            data['cores'][core]['scheduler']['sync'] = value;
          });
        },
      ),
    );
    insertPadding(children);
    if (data['switches']['performanceScheduling']) {
      children.add(
          // preemptTick
          CustomFormField(
        onChanged: (String value) {
          data['cores'][core]['scheduler']['preemptTick'] = value;
        },
        controller: _generateController(
            data['cores'][core]['scheduler']['preemptTick']),
        label: 'preemptTick',
        validator: () {},
      ));
    }

    // table
    // _schedulerTablesBuilder(children, core);
  }

  void _sysJobsGroupBuilder(List<Widget> children, String core, String group) {
    _arrowDropDown(children, group, space: 100.0);

    if (visibleWindows[group] != null && visibleWindows[group]!) {
      insertPadding(children);

      // tickMultiplicator
      children.add(CustomFormField(
        onChanged: (String value) {
          data['cores'][core]['sysJobs']['groups'][group]['tickMultiplicator'] =
              value;
        },
        controller: _generateController(data['cores'][core]['sysJobs']['groups']
            [group]['tickMultiplicator']),
        label: 'tickMultiplicator',
        validator: () {},
      ));
      insertPadding(children);

      children.add(Padding(
        padding: const EdgeInsets.only(top: 8.0, bottom: 8.0),
        child: Text('handlers:', style: TextStyle(fontSize: 14.0)),
      ));

      data['cores'][core]['sysJobs']['groups'][group]['handlers']
          .asMap()
          .forEach((index, handler) {
        children.add(Padding(
          padding: const EdgeInsets.only(left: 8.0),
          child: Text('$index. $handler'),
        ));
      });

      children.add(_addHandlerButton(core, group));

      children.add(Padding(
        padding: const EdgeInsets.only(top: 8.0, bottom: 8.0),
        child: Text('api_headers:', style: TextStyle(fontSize: 14.0)),
      ));

      data['cores'][core]['sysJobs']['groups'][group]['api_headers']
          .asMap()
          .forEach((index, apiHeader) {
        children.add(Padding(
          padding: const EdgeInsets.only(left: 8.0),
          child: Text('$index. $apiHeader'),
        ));
      });

      children.add(_addAPIHeaderButton(core, group));
    }
  }

  void _schedulerTablesBuilder(List<Widget> children, String core) {
    children.add(Padding(
      padding: const EdgeInsets.only(top: defaultPadding, bottom: 8.0),
      child: Text(
        "table:",
        style: TextStyle(fontSize: 20.0),
      ),
    ));

    data['cores'][core]['scheduler']['table'].forEach((element, val) {
      children.add(Padding(
          padding: const EdgeInsets.only(top: 8.0, bottom: 8.0),
          child: Text(
            element,
            style: TextStyle(fontSize: 16.0),
          )));

      children.add(Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          Padding(
            padding: const EdgeInsets.only(right: 4.0, top: 4.0, bottom: 4.0),
            child: Container(
                width: 230.0,
                child: CustomDropDownField(
                  value: int.parse(data['cores'][core]['scheduler']['table']
                      [element]['core']),
                  items: generateDropDownItems(data['cores']),
                  label: 'core',
                  onChanged: (value) {
                    data['cores'][core]['scheduler']['table'][element]['core'] =
                        value.toString();
                    setState(() {});
                  },
                )),
          ),
          Padding(
            padding: const EdgeInsets.only(right: 4.0, top: 4.0, bottom: 4.0),
            child: Container(
                width: 230.0,
                child: CustomDropDownField(
                  value: int.parse(data['cores'][core]['scheduler']['table']
                      [element]['program']),
                  items: generateDropDownItems(data['cores'][core]['programs']),
                  label: 'program',
                  onChanged: (value) {
                    data['cores'][core]['scheduler']['table'][element]
                        ['program'] = value.toString();
                    setState(() {});
                  },
                )),
          )
        ],
      ));

      insertPadding(children);

      children.add(Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          Padding(
            padding: const EdgeInsets.only(right: 4.0, top: 4.0, bottom: 4.0),
            child: Container(
                width: 230.0,
                child: CustomDropDownField(
                  value: int.parse(data['cores'][core]['scheduler']['table']
                      [element]['task']),
                  items: generateDropDownItems(data['cores'][core]['programs'][
                          'program_${data['cores'][core]['scheduler']['table'][element]['program']}']
                      ['tasks']),
                  label: 'task',
                  onChanged: (value) {
                    data['cores'][core]['scheduler']['table'][element]['task'] =
                        value.toString();
                    setState(() {});
                  },
                )),
          ),
          Padding(
            padding: const EdgeInsets.only(right: 4.0, top: 4.0, bottom: 4.0),
            child: Container(
              width: 230.0,
              child: CustomFormField(
                onChanged: (value) {
                  data['cores'][core]['scheduler']['table'][element]
                      ['executionTick'] = value;
                },
                controller: _generateController(data['cores'][core]['scheduler']
                    ['table'][element]['executionTick']),
                label: 'executionTick',
                validator: () {},
              ),
            ),
          )
        ],
      ));
    });
  }

  void _sysJobsGroupsBuilder(List<Widget> children, String core) {
    children.add(Padding(
      padding: const EdgeInsets.only(top: 8.0, bottom: 8.0),
      child: Text(
        "groups:",
        style: TextStyle(fontSize: 20.0),
      ),
    ));

    data['cores'][core]['sysJobs']['groups'].forEach((group, val) {
      _sysJobsGroupBuilder(children, core, group);
    });

    children.add(_addGroupButton(core));
  }

  void _sysJobsBuilder(List<Widget> children, String core) {
    // hyperTick
    children.add(CustomFormField(
      onChanged: (String value) {
        data['cores'][core]['sysJobs']['hyperTick'] = value;
      },
      controller:
          _generateController(data['cores'][core]['sysJobs']['hyperTick']),
      label: 'hyperTick',
      validator: () {},
    ));
    insertPadding(children);

    _sysJobsGroupsBuilder(children, core);
  }

  void _unmappedBuilder(List<Widget> children, String core) {
    children.add(Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Container(
          width: 270.0,
          child: CustomDropDownField(
            value: data['cores'][core]['unmapped']['size'] != null
                ? int.parse(data['cores'][core]['unmapped']['size'])
                : null,
            items: generatePowerOfTwoItems(),
            label: 'size',
            onChanged: (value) {
              data['cores'][core]['unmapped']['size'] = value.toString();
              setState(() {});
            },
          ),
        ),
        Container(
          width: 270.0,
          child: CustomDropDownField(
              value: data['cores'][core]['unmapped']['memory'],
              items: memoryTypes
                  .map((item) => DropdownMenuItem(
                        child: Text(item),
                        value: item,
                      ))
                  .toList(),
              label: 'memory',
              onChanged: (value) {
                data['cores'][core]['unmapped']['memory'] = value;
              }),
        )
      ],
    ));
    // size

    insertPadding(children);
  }

  Widget _coreBuilder(String core) {
    List<Widget> children = [];

    // name
    children.add(CustomFormField(
      onChanged: (String value) {
        data['cores'][core]['name'] = value;
      },
      controller: _generateController(data['cores'][core]['name']),
      label: 'name',
      validator: () {},
    ));

    insertPadding(children);

    // bootOs
    children.add(Text('bootOs:'));
    children.add(
      Checkbox(
        value: data['cores'][core]['bootOs'],
        onChanged: (bool? value) {
          if (value == null) {
            return;
          }
          if (value) {
            _unselectBootUpCores();
          }

          setState(() {
            data['cores'][core]['bootOs'] = value;
          });
        },
      ),
    );

    children.add(Container(
      margin: EdgeInsets.symmetric(vertical: 20.0),
      height: 50.0,
      child: ListView(
        scrollDirection: Axis.horizontal,
        children: <Widget>[
          Container(
            width: 145.0,
            child: GestureDetector(
              onTap: () {
                setState(() {
                  _coreDetailTab = CoreDetailTab.Programs;
                });
              },
              child: Card(
                  color: _coreDetailTab == CoreDetailTab.Programs
                      ? Color(0xff313131)
                      : tertiaryColor,
                  child: Align(
                      alignment: Alignment.center, child: Text("programs"))),
            ),
          ),
          Container(
            width: 145.0,
            child: GestureDetector(
              onTap: () {
                setState(() {
                  _coreDetailTab = CoreDetailTab.Scheduler;
                });
              },
              child: Card(
                  color: _coreDetailTab == CoreDetailTab.Scheduler
                      ? Color(0xff313131)
                      : tertiaryColor,
                  child: Align(
                      alignment: Alignment.center, child: Text("scheduler"))),
            ),
          ),
          Container(
            width: 145.0,
            child: GestureDetector(
              onTap: () {
                setState(() {
                  _coreDetailTab = CoreDetailTab.SystemJobs;
                });
              },
              child: Card(
                  color: _coreDetailTab == CoreDetailTab.SystemJobs
                      ? Color(0xff313131)
                      : tertiaryColor,
                  child: Align(
                      alignment: Alignment.center, child: Text("sysJobs"))),
            ),
          ),
          Container(
            width: 145.0,
            child: GestureDetector(
              onTap: () {
                setState(() {
                  _coreDetailTab = CoreDetailTab.Unmapped;
                });
              },
              child: Card(
                  color: _coreDetailTab == CoreDetailTab.Unmapped
                      ? Color(0xff313131)
                      : tertiaryColor,
                  child: Align(
                      alignment: Alignment.center, child: Text("unmapped"))),
            ),
          )
        ],
      ),
    ));

    if (_coreDetailTab == CoreDetailTab.Programs) {
      _programsBuilder(children, core);
    } else if (_coreDetailTab == CoreDetailTab.Scheduler) {
      _schedulerBuilder(children, core);
    } else if (_coreDetailTab == CoreDetailTab.SystemJobs) {
      _sysJobsBuilder(children, core);
    } else {
      _unmappedBuilder(children, core);
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: children,
    );
  }

  Widget _coresBuilder() {
    List<Widget> children = [];
    _setData();

    data['cores'].forEach((key, val) {
      _arrowDropDown(children, key, fontSize: 18.0);

      if (visibleWindows[key] != null && visibleWindows[key]!) {
        children.add(
          Flexible(
            fit: FlexFit.loose,
            flex: 6,
            child: Container(
                decoration: BoxDecoration(
                    color: secondaryColor,
                    borderRadius: BorderRadius.all(Radius.circular(10.0))),
                width: 600,
                child: Padding(
                  padding: const EdgeInsets.all(defaultPadding),
                  child: _coreBuilder(key),
                )),
          ),
        );
        insertPadding(children, height: 30.0);
      }
    });

    return Form(
      key: _formKey,
      child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: children),
    );
  }

  List<Widget> _awaitingResultBuilder() {
    return <Widget>[
      SizedBox(
        child: CircularProgressIndicator(),
        width: 60,
        height: 60,
      ),
      Padding(
        padding: EdgeInsets.only(top: 16),
        child: Text('Awaiting result...'),
      )
    ];
  }

  List<Widget> _errorBuilder(data) {
    return <Widget>[
      const Icon(
        Icons.error_outline,
        color: Colors.red,
        size: 60,
      ),
      Padding(
        padding: const EdgeInsets.only(top: 16),
        child: Text('Error: ${data.error}'),
      )
    ];
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<dynamic>(
      future: _getConfigFiles(),
      builder: (BuildContext context, AsyncSnapshot<dynamic> snapshot) {
        List<Widget> children = [];
        if (snapshot.hasData) {
          children = [_coresBuilder()];
        } else if (snapshot.hasError) {
          children = _errorBuilder(snapshot);
        } else {
          children = _awaitingResultBuilder();
        }
        return Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: children,
        );
      },
    );
  }

  Future<dynamic> _getConfigFiles() async {
    if (mcuData.isEmpty) {
      mcuData = await ConfigService.instance.readJson(context, ConfigFile.MCU);
    }

    if (sysJobsData.isEmpty) {
      sysJobsData =
          await ConfigService.instance.readJson(context, ConfigFile.SystemJobs);
    }

    return {'mcu': mcuData, 'sysJobs': sysJobsData};
  }
}
