import 'package:cosmos_config_controller/pages/cosmos/components/config_screens/buffers.dart';
import 'package:cosmos_config_controller/pages/cosmos/components/config_screens/cores.dart';
import 'package:cosmos_config_controller/pages/cosmos/components/config_screens/switches.dart';
import 'package:cosmos_config_controller/pages/cosmos/components/config_screens/syscalls.dart';
import 'package:cosmos_config_controller/data/config_service.dart';
import 'package:cosmos_config_controller/utils/config_inherited_widget.dart';
import 'package:cosmos_config_controller/utils/responsive.dart';
import 'package:cosmos_config_controller/utils/toaster_mixin.dart';
import 'package:cosmos_config_controller/pages/cosmos/components/dashboard.dart';
import 'package:cosmos_config_controller/pages/cosmos/components/side_navbar.dart';
import 'package:flutter/material.dart';

// TODO: enable to add object, which might not exist (dropdown default value)

enum ConfigScreen { Cores, Buffers, Switches, SystemCalls }

class CosmosConfigPage extends StatefulWidget {
  CosmosConfigPage();

  @override
  _CosmosConfigState createState() => _CosmosConfigState();
}

class _CosmosConfigState extends State<CosmosConfigPage> with Toaster {
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  Map<String, dynamic> json = {};
  ConfigScreen _configScreen = ConfigScreen.Buffers;

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

  void _onUpdateConfigScreen(ConfigScreen configScreen) {
    setState(() {
      this._configScreen = configScreen;
    });
  }

  Widget _configScreenSwitch() {
    if (_configScreen == ConfigScreen.Cores) {
      return Dashboard(configScreen: Cores(), title: Cores.title);
    } else if (_configScreen == ConfigScreen.Buffers) {
      return Dashboard(configScreen: Buffers(), title: Buffers.title);
    } else if (_configScreen == ConfigScreen.Switches) {
      return Dashboard(configScreen: Switches(), title: Switches.title);
    } else {
      return Dashboard(configScreen: Syscalls(), title: Syscalls.title);
    }
  }

  List<Widget> _successBuilder() {
    return <Widget>[
      if (Responsive.isDesktop(context))
        Expanded(
          flex: 1,
          child: SideNavBar(
            version: json['CosmOSVersion'],
            configScreenSelected: _configScreen,
            onScreenChange: (ConfigScreen configScreen) {
              _onUpdateConfigScreen(configScreen);
            },
          ),
        ),
      ConfigInheritedWidget(
          Expanded(
            flex: 5,
            child: _configScreenSwitch(),
          ),
          json)
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        key: _scaffoldKey,
        body: SafeArea(
          child: FutureBuilder<dynamic>(
            future: ConfigService.instance.readJson(context, ConfigFile.CosmOS),
            builder: (BuildContext context, AsyncSnapshot<dynamic> snapshot) {
              List<Widget> children;
              if (snapshot.hasData) {
                if (json.isEmpty) {
                  json = snapshot.data;
                }
                children = _successBuilder();
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
          ),
        ));
  }
}
