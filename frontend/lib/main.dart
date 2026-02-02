import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const JanSathiApp());
}

class JanSathiApp extends StatelessWidget {
  const JanSathiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'JanSathi',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.orange),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
