import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'dart:async';

import '../services/api_service.dart';
import '../services/offline_service.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late AudioRecorder _audioRecorder;
  final ApiService _apiService = ApiService();
  final OfflineService _offlineService = OfflineService();
  final TextEditingController _textController = TextEditingController();

  bool _isRecording = false;
  bool _isLoading = false;
  String _statusText = "Tap Mic to Speak or Type Query";
  String _responseText = "";

  // Stream state for Web compatibility
  StreamSubscription<List<int>>? _micStream;
  List<int> _audioBytes = [];

  @override
  void initState() {
    super.initState();
    _audioRecorder = AudioRecorder();
  }

  @override
  void dispose() {
    _audioRecorder.dispose();
    _micStream?.cancel();
    _textController.dispose();
    super.dispose();
  }

  // ---------------- Voice Logic ----------------
  Future<void> _startRecording() async {
    try {
      final status = await Permission.microphone.request();
      if (!status.isGranted) {
        setState(() => _statusText = "Microphone permission denied");
        return;
      }

      if (await _audioRecorder.hasPermission()) {
        _audioBytes = [];

        final stream = await _audioRecorder.startStream(
          const RecordConfig(encoder: AudioEncoder.pcm16bits),
        );

        _micStream = stream.listen((data) {
          _audioBytes.addAll(data);
        });

        setState(() {
          _isRecording = true;
          _statusText = "Listening...";
          _responseText = "";
        });
      }
    } catch (e) {
      _handleError(e);
    }
  }

  Future<void> _stopRecording() async {
    try {
      await _audioRecorder.stop();
      await _micStream?.cancel();

      setState(() {
        _isRecording = false;
        _isLoading = true;
        _statusText = "Processing Audio...";
      });

      if (_audioBytes.isEmpty) {
        setState(() {
          _isLoading = false;
          _statusText = "No audio recorded";
        });
        return;
      }

      final response = await _apiService.sendVoiceQuery(_audioBytes);
      _handleResponse(response);
    } catch (e) {
      _handleError(e);
    }
  }

  // ---------------- Text Logic ----------------
  Future<void> _sendText() async {
    if (_textController.text.trim().isEmpty) return;

    FocusScope.of(context).unfocus();

    setState(() {
      _isLoading = true;
      _responseText = "";
      _statusText = "Processing Text...";
    });

    final connectivity = await Connectivity().checkConnectivity();
    if (connectivity == ConnectivityResult.none) {
      final offlineAnswer = _offlineService.search(_textController.text);
      setState(() {
        _responseText = offlineAnswer ??
            "You are offline. Try asking about ration, health, or kisan schemes.";
        _statusText = "Offline Mode";
        _isLoading = false;
      });
      _textController.clear();
      return;
    }

    try {
      final response = await _apiService.sendTextQuery(_textController.text);
      _handleResponse(response);
      _textController.clear();
    } catch (e) {
      _handleError(e);
    }
  }

  // ---------------- Common Handlers ----------------
  void _handleResponse(Map<String, dynamic> response) {
    setState(() {
      _responseText = response['answer'] ?? "No answer received.";
      _statusText = "Query Complete";
      _isLoading = false;
    });
  }

  void _handleError(Object e) {
    setState(() {
      _responseText = "Error: ${e.toString()}";
      _statusText = "Tap to retry";
      _isLoading = false;
    });
  }

  // ---------------- UI ----------------
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('JanSathi (Digital Assistant)'),
        backgroundColor: Colors.orange,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (_responseText.isNotEmpty)
              Container(
                padding: const EdgeInsets.all(16),
                margin: const EdgeInsets.only(bottom: 20),
                decoration: BoxDecoration(
                  color: Colors.orange.shade50,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.orange.shade200),
                ),
                child: Text(
                  _responseText,
                  style: const TextStyle(fontSize: 16, color: Colors.black87),
                ),
              ),
            const SizedBox(height: 20),
            Center(
              child: Text(
                _statusText,
                style: const TextStyle(fontSize: 16, color: Colors.grey),
              ),
            ),
            const SizedBox(height: 30),
            Center(
              child: GestureDetector(
                onTap: _isLoading
                    ? null
                    : (_isRecording ? _stopRecording : _startRecording),
                child: Container(
                  width: 100,
                  height: 100,
                  decoration: BoxDecoration(
                    color: _isLoading
                        ? Colors.grey
                        : (_isRecording ? Colors.red : Colors.blue),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    _isLoading
                        ? Icons.hourglass_bottom
                        : (_isRecording ? Icons.stop : Icons.mic),
                    color: Colors.white,
                    size: 40,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 40),
            const Divider(),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _textController,
                    enabled: !_isLoading,
                    decoration: InputDecoration(
                      hintText: "Type your query here...",
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(30),
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 15,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                IconButton(
                  icon: const Icon(Icons.send, size: 30),
                  onPressed: _isLoading ? null : _sendText,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
