import 'package:cosmos_config_controller/utils/constants.dart';
import 'package:flutter/material.dart';

mixin Toaster {

  void displayMessage(BuildContext context, String message) {
    final SnackBar snackBar = SnackBar(
      content: RichText(
        text: TextSpan(
          children: [
            WidgetSpan(
              child: Icon(Icons.check_box, color: secondaryColor, size: 18.0),
            ),
            TextSpan(
              text: message,
              style: TextStyle(color: secondaryColor),
            ),
          ]
        )
      ),
      backgroundColor: Color(0xff64ffda),
    );
    ScaffoldMessenger.of(context).showSnackBar(snackBar);
  }

  void displayErrorMessage(BuildContext context, String message) {
    final SnackBar snackBar = SnackBar(
      content: RichText(
          text: TextSpan(
              children: [
                WidgetSpan(
                  child: Icon(Icons.error, color: Colors.white, size: 18.0),
                ),
                TextSpan(
                    text: message,
                    style: TextStyle(color: Colors.white)
                ),
              ]
          )
      ),      backgroundColor: Color(0xFF84073D),
    );
    ScaffoldMessenger.of(context).showSnackBar(snackBar);
  }

}