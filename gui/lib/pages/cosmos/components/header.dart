import 'dart:ffi';

import 'package:cosmos_config_controller/data/config_service.dart';
import 'package:cosmos_config_controller/utils/config_inherited_widget.dart';
import 'package:cosmos_config_controller/utils/constants.dart';
import 'package:cosmos_config_controller/utils/toaster_mixin.dart';
import 'package:flutter/material.dart';

class Header extends StatelessWidget with Toaster {
  const Header({
    Key? key,
    required this.title,
  }) : super(key: key);

  final String title;

  bool validate(Map<String, dynamic> data, BuildContext context) {
    var errors = [];

    data['cores'].forEach((key, value) {});

    data['buffers'].forEach((bufferKey, buffer) {
      buffer.forEach((key, value) {
        if (value is bool || value is Array || value is List) {
          return;
        }
        if (value is Map) {
          // if (value.containsKey('name')) {
          //   if (value['name'] == null || value['name'].isEmpty) {
          //     errors.add("$bufferKey $key name");
          //   }
          // }

          value.forEach((k, v) {
            if (v == null || v.isEmpty) {
              errors.add("$bufferKey $key name");
            }
            print(v);
          });
          // print(key);
          // print(value);
          // value['tasksReadPermissions'].forEach((k, v) {

          // });
        }

        if (value == null || value.isEmpty) {
          errors.add("$bufferKey $key");
        }
      });
    });

    data['sysCalls']['routed_funcs'].forEach((function, values) {
      values.forEach((valueKey, value) {
        if (value is bool || value is Array || value is List) {
          return;
        }
        if (value == null || value.isEmpty) {
          errors.add("$function $valueKey");
        }
      });
    });

    print(errors);

    return false;
  }

  Future<void> _onConfigSave(BuildContext context) async {
    final Map<String, dynamic> data = ConfigInheritedWidget.of(context).json;

    validate(data, context);

    bool isSaved =
        await ConfigService.instance.writeJson(data, ConfigFile.CosmOS);

    if (isSaved) {
      displayMessage(context, "systemModelCfg.json has been updated");
    } else {
      displayErrorMessage(context, "systemModelCfg.json update has failed");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: Theme.of(context).textTheme.headline6,
              ),
              Padding(
                padding: const EdgeInsets.only(bottom: 4.0),
                child: Container(
                  height: 35.0,
                  width: 120.0,
                  child: TextButton(
                      onPressed: () async {
                        _onConfigSave(context);
                      },
                      style: ButtonStyle(
                        backgroundColor: MaterialStateProperty.all<Color>(
                            sideNavActiveColor),
                        foregroundColor:
                            MaterialStateProperty.all<Color>(Colors.white),
                      ),
                      child: Text("Save Config")),
                ),
              )
            ],
          ),
          Padding(
            padding: EdgeInsets.only(top: 4.0),
            child: Container(
              color: secondaryColor,
              height: 2.0,
            ),
          )
        ],
      ),
    );
  }
}
