import 'package:flutter/material.dart';

class CustomDropDownField extends StatelessWidget {
  final onChanged;
  final String label;
  final dynamic value;
  final List<DropdownMenuItem> items;

  const CustomDropDownField(
      {Key? key,
      required this.label,
      this.value,
      required this.onChanged,
      required this.items})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return DropdownButtonFormField(
      value: value,
      items: items,
      onChanged: onChanged,
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
