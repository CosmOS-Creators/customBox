import 'package:cosmos_config_controller/routing/route_generator.dart';
import 'package:cosmos_config_controller/routing/routes.dart';
import 'package:cosmos_config_controller/utils/constants.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';


void main() {
  runApp(App());
}

class App extends StatelessWidget {
  static const String title = "CosmOS";

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: title,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: bgColor,
        canvasColor: secondaryColor,
        textTheme: GoogleFonts.poppinsTextTheme(
            Theme.of(context).textTheme
        ).apply(bodyColor: Colors.white),
      ),
      debugShowCheckedModeBanner: false,
      initialRoute: AppRoute.ROOT_ROUTE,
      onGenerateRoute: RouteGenerator.generateRoute,
    );
  }
}
