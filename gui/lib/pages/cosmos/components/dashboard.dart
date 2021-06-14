import 'package:cosmos_config_controller/utils/constants.dart';
import 'package:cosmos_config_controller/pages/cosmos/components/header.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class Dashboard extends StatelessWidget {
  const Dashboard({
    Key? key,
    required this.title,
    required this.configScreen,
  }) : super(key: key);

  final String title;
  final Widget configScreen;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: EdgeInsets.all(defaultPadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
          Header(title: title),
          Padding(
            padding: EdgeInsets.only(top: defaultPadding),
            child: configScreen,
          ),
        ],
      ),
    );
  }
}
