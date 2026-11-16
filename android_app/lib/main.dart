import 'package:flutter/material.dart';
import 'theme/colors.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const ForgeApp());
}

class ForgeApp extends StatelessWidget {
  const ForgeApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FORGE 2.0',
      debugShowCheckedModeBanner: false,
      themeMode: ThemeMode.dark,
      darkTheme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        scaffoldBackgroundColor: ForgeColors.background,
        colorScheme: const ColorScheme.dark(
          primary: ForgeColors.flamePrimary,
          secondary: ForgeColors.purpleAccent,
          surface: ForgeColors.surface,
          background: ForgeColors.background,
        ),
      ),
      home: const HomeScreen(),
    );
  }
}
