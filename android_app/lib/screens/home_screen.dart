import 'package:flutter/material.dart';
import '../theme/colors.dart';
import 'dashboard_screen.dart';
import 'planner_screen.dart';
import 'focus_screen.dart';
import 'analytics_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    DashboardScreen(),
    PlannerScreen(),
    FocusScreen(),
    AnalyticsScreen(),
    SettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: ForgeColors.background,
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: NavigationBarTheme(
        data: NavigationBarThemeData(
          backgroundColor: ForgeColors.surface.withOpacity(0.9),
          indicatorColor: ForgeColors.flamePrimary.withOpacity(0.2),
          labelTextStyle: MaterialStateProperty.all(
            const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: ForgeColors.textSecondary),
          ),
        ),
        child: NavigationBar(
          selectedIndex: _currentIndex,
          onDestinationSelected: (idx) => setState(() => _currentIndex = idx),
          destinations: const [
            NavigationDestination(
              icon: Icon(Icons.dashboard_outlined, color: ForgeColors.textSecondary),
              selectedIcon: Icon(Icons.dashboard, color: ForgeColors.flamePrimary),
              label: 'Today',
            ),
            NavigationDestination(
              icon: Icon(Icons.calendar_today_outlined, color: ForgeColors.textSecondary),
              selectedIcon: Icon(Icons.calendar_today, color: ForgeColors.flamePrimary),
              label: 'Planner',
            ),
            NavigationDestination(
              icon: Icon(Icons.timer_outlined, color: ForgeColors.textSecondary),
              selectedIcon: Icon(Icons.timer, color: ForgeColors.flamePrimary),
              label: 'Focus',
            ),
            NavigationDestination(
              icon: Icon(Icons.insights_outlined, color: ForgeColors.textSecondary),
              selectedIcon: Icon(Icons.insights, color: ForgeColors.flamePrimary),
              label: 'Analytics',
            ),
            NavigationDestination(
              icon: Icon(Icons.settings_outlined, color: ForgeColors.textSecondary),
              selectedIcon: Icon(Icons.settings, color: ForgeColors.flamePrimary),
              label: 'Settings',
            ),
          ],
        ),
      ),
    );
  }
}
