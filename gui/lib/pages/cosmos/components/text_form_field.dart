import 'package:flutter/material.dart';

class CustomFormField extends StatelessWidget {
  final ValueChanged<String> onChanged;
  final Function validator;
  final TextEditingController controller;
  final String label;

  const CustomFormField({
    Key? key,
    required this.label,
    required this.onChanged,
    required this.validator,
    required this.controller,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      cursorColor: Colors.white10,
      controller: controller,
      onChanged: onChanged,
      // validator: validator,
      decoration: InputDecoration(
        enabledBorder: const OutlineInputBorder(
          borderSide: const BorderSide(color: Colors.white, width: 0.0),
        ),
        focusedBorder: const OutlineInputBorder(
          borderSide: const BorderSide(color: Colors.grey, width: 0.0),
        ),
        labelText: label,
        labelStyle: TextStyle(fontSize: 17.0, color: Colors.white60),
        border: OutlineInputBorder(),
      ),
    );
  }
}
