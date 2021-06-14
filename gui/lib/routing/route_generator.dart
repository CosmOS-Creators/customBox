import 'package:cosmos_config_controller/routing/routes.dart';
import 'package:cosmos_config_controller/utils/constants.dart';
import 'package:cosmos_config_controller/utils/error_messages.dart';
import 'package:cosmos_config_controller/pages/cosmos/cosmos_config.dart';
import 'package:flutter/material.dart';


class RouteGenerator {

  static Route<dynamic> generateRoute (RouteSettings settings) {
    switch (settings.name) {

      case AppRoute.ROOT_ROUTE:
        return MaterialPageRoute(builder: (_) => CosmosConfigPage());

      default:
        return _errorRoute();
    }
  }

  static Route<dynamic> _errorRoute() {
    return MaterialPageRoute(builder: (_) {
      return Scaffold(
        backgroundColor: primaryColor,
        appBar: AppBar(
          title: Text(ErrorMessage.NAVIGATION_FAILED_HEADER),
        ),
        body: Center(
          child: Text(ErrorMessage.NAVIGATION_FAILED),
        ),
      );
    });
  }
}

