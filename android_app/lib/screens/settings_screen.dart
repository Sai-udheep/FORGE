import 'package:flutter/material.dart';
import '../theme/colors.dart';
import '../theme/glass_theme.dart';
import '../services/api_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({Key? key}) : super(key: key);

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final ApiService _api = ApiService();
  final TextEditingController _urlCtrl = TextEditingController();
  bool _saved = false;

  @override
  void initState() {
    super.initState();
    _loadUrl();
  }

  void _loadUrl() async {
    final url = await _api.getBaseUrl();
    _urlCtrl.text = url;
  }

  void _saveUrl() async {
    await _api.setBaseUrl(_urlCtrl.text);
    setState(() => _saved = true);
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) setState(() => _saved = false);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: ForgeColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('SETTINGS & SYNC', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'FORGE BACKEND LAN CONNECTION',
                  style: TextStyle(
                    color: ForgeColors.textSecondary,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _urlCtrl,
                  style: const TextStyle(color: ForgeColors.textPrimary),
                  decoration: InputDecoration(
                    labelText: 'Backend URL',
                    labelStyle: const TextStyle(color: ForgeColors.textSecondary),
                    hintText: 'http://192.168.1.xxx:8000/api/v1',
                    hintStyle: const TextStyle(color: ForgeColors.textMuted),
                    filled: true,
                    fillColor: ForgeColors.surface,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
                const SizedBox(height: 12),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: ForgeColors.flamePrimary,
                    foregroundColor: Colors.white,
                  ),
                  onPressed: _saveUrl,
                  child: Text(_saved ? '✅ Saved!' : 'Save Connection'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: const [
                Text(
                  'SYSTEM INFORMATION',
                  style: TextStyle(
                    color: ForgeColors.textSecondary,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 12),
                Text('FORGE 2.0 Mobile Client v2.0.0', style: TextStyle(color: ForgeColors.textPrimary)),
                SizedBox(height: 4),
                Text('Design: macOS Sequoia Liquid Glassmorphism', style: TextStyle(color: ForgeColors.textSecondary)),
                SizedBox(height: 4),
                Text('Study Cursor Integration: Active (Read-Only + Explicit Confirm)', style: TextStyle(color: ForgeColors.emeraldGreen)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
