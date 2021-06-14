import 'package:flutter/material.dart';

final ButtonStyle textButtonStyle = TextButton.styleFrom(
  backgroundColor: Colors.black54,
  primary: Colors.white,
  minimumSize: Size(88, 36),
  padding: EdgeInsets.symmetric(horizontal: 16.0),
  shape: const RoundedRectangleBorder(
    borderRadius: BorderRadius.all(Radius.circular(2.0)),
  ),
);