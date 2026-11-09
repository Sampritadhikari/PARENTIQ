import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/theme/app_theme.dart';
import 'screens/auth/login_screen.dart';
import 'screens/main_navigation_screen.dart';
import 'services/api_service.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ApiService()),
      ],
      child: const ParentIQApp(),
    ),
  );
}

class ParentIQApp extends StatefulWidget {
  const ParentIQApp({super.key});

  @override
  State<ParentIQApp> createState() => _ParentIQAppState();
}

class _ParentIQAppState extends State<ParentIQApp> {
  bool _isLoggedIn = false;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PARENTIQ',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.light,
      home: _isLoggedIn
          ? MainNavigationScreen(
              onLogout: () {
                context.read<ApiService>().logout();
                setState(() => _isLoggedIn = false);
              },
            )
          : LoginScreen(
              onLoginSuccess: () {
                setState(() => _isLoggedIn = true);
              },
            ),
    );
  }
}

