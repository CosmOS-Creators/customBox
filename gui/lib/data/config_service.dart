import 'dart:convert';
import 'dart:io';

import 'package:cosmos_config_controller/utils/constants.dart';
import 'package:flutter/cupertino.dart';

enum ConfigFile { CosmOS, SystemCalls, MCU, SystemJobs }

abstract class ConfigService {
  static final ConfigService instance = ConfigServiceImpl();
  ConfigFile configFile = ConfigFile.CosmOS;

  Future<bool> writeJson(Map<String, dynamic> json, ConfigFile configFile);
  Future<dynamic> readJson(BuildContext context, ConfigFile configFile);
}

class ConfigServiceImpl extends ConfigService {
  Future<File> get _cosmosConfigFile async {
    return File(cosmosConfigPath);
  }

  Future<File> get _syscallsConfigFile async {
    return File(syscallsConfigPath);
  }

  Future<File> get _mcuConfigFile async {
    return File(mcuConfigPath);
  }

  Future<File> get _systemJobsConfigFile async {
    return File(systemJobsConfigPath);
  }

  Future<File> _configFileSwitch(ConfigFile configFile) {
    if (configFile == ConfigFile.CosmOS) {
      return _cosmosConfigFile;
    } else if (configFile == ConfigFile.SystemCalls) {
      return _syscallsConfigFile;
    } else if (configFile == ConfigFile.SystemJobs) {
      return _systemJobsConfigFile;
    } else {
      return _mcuConfigFile;
    }
  }

  Future<bool> writeJson(
      Map<String, dynamic> json, ConfigFile configFile) async {
    if (json.isEmpty) {
      return false;
    }

    File file = await _configFileSwitch(configFile);

    final String decodedJson = jsonEncode(json);

    file = await file.writeAsString(decodedJson);

    return true;
  }

  Future<dynamic> readJson(BuildContext context, ConfigFile configFile) async {
    try {
      File file = await _configFileSwitch(configFile);
      String encodedJson =
          await DefaultAssetBundle.of(context).loadString(file.path);

      if (encodedJson.isEmpty) {
        print("_readJson: File doesn't exists");
        return null;
      }

      dynamic json = jsonDecode(encodedJson);

      return json;
    } catch (e) {
      print("_readJson: Tried reading file error: $e");
    }

    return null;
  }
}
