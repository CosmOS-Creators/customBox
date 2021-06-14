import 'package:cosmos_config_controller/main.dart';
import 'package:cosmos_config_controller/pages/cosmos/cosmos_config.dart';
import 'package:cosmos_config_controller/utils/constants.dart';
import 'package:flutter/material.dart';

class SideNavBar extends StatelessWidget {
  const SideNavBar(
      {Key? key,
      required this.version,
      required this.onScreenChange,
      required this.configScreenSelected})
      : super(key: key);

  final String version;
  final Function onScreenChange;
  final ConfigScreen configScreenSelected;

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: SingleChildScrollView(
        child: Column(
          children: [
            DrawerHeader(
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Text(
                      App.title,
                      style: TextStyle(fontSize: 22.0),
                    ),
                    Text("v$version")
                  ],
                ),
              ),
            ),
            DrawerListTile(
              title: "Cores",
              selected: configScreenSelected == ConfigScreen.Cores,
              press: () {
                onScreenChange(ConfigScreen.Cores);
              },
            ),
            DrawerListTile(
              title: "Buffers",
              selected: configScreenSelected == ConfigScreen.Buffers,
              press: () {
                onScreenChange(ConfigScreen.Buffers);
              },
            ),
            DrawerListTile(
              title: "Switches",
              selected: configScreenSelected == ConfigScreen.Switches,
              press: () {
                onScreenChange(ConfigScreen.Switches);
              },
            ),
            DrawerListTile(
              title: "Syscalls",
              selected: configScreenSelected == ConfigScreen.SystemCalls,
              press: () {
                onScreenChange(ConfigScreen.SystemCalls);
              },
            ),
          ],
        ),
      ),
    );
  }
}

class DrawerListTile extends StatelessWidget {
  const DrawerListTile({
    Key? key,
    required this.title,
    required this.press,
    required this.selected,
  }) : super(key: key);

  final String title;
  final VoidCallback press;
  final bool selected;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      onTap: press,
      selected: selected,
      horizontalTitleGap: 0.0,
      selectedTileColor: sideNavActiveColor,
      title: Text(
        title,
        style: TextStyle(color: Colors.white54),
      ),
    );
  }
}
