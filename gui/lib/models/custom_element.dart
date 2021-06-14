class CustomElement {
  final int id;
  final int coreID;
  final int programID;
  final String name;

  CustomElement(
      {required this.id,
      required this.coreID,
      required this.programID,
      required this.name});

  @override
  String toString() {
    return "id: $id, coreID: $coreID, programID: $programID, name: $name";
  }

  bool operator ==(dynamic other) =>
      other != null && other is CustomElement && other.name == name;

  @override
  int get hashCode => super.hashCode;
}
