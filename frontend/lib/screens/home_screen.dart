import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import '../services/api_service.dart';
import 'package:permission_handler/permission_handler.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late AudioRecorder _audioRecorder;
  final AudioPlayer _audioPlayer = AudioPlayer();
  final ApiService _apiService = ApiService();
  
  bool _isRecording = false;
  bool _isLoading = false;
  String _statusText = "Tap to Speak";
  String _responseText = "";
  String? _recordedPath;

  @override
  void initState() {
    super.initState();
    _audioRecorder = AudioRecorder();
  }

  @override
  void dispose() {
    _audioRecorder.dispose();
    _audioPlayer.dispose();
    super.dispose();
  }

  Future<void> _startRecording() async {
    try {
      if (await _audioRecorder.hasPermission()) {
        final directory = await getTemporaryDirectory();
        final path = '${directory.path}/my_audio.wav';
        
        await _audioRecorder.start(const RecordConfig(), path: path);
        
        setState(() {
          _isRecording = true;
          _statusText = "Listening...";
          _responseText = "";
        });
        _recordedPath = path;
      }
    } catch (e) {
      print(e);
    }
  }

  Future<void> _stopRecording() async {
    try {
      final path = await _audioRecorder.stop();
      setState(() {
        _isRecording = false;
        _isLoading = true;
        _statusText = "Processing...";
      });

      if (path != null) {
        final response = await _apiService.sendVoiceQuery(path);
        
        setState(() {
          _responseText = response['answer'] ?? "No answer received.";
          _statusText = "Tap to Speak";
          _isLoading = false;
        });

        // Play audio if backend sends URL (not implemented in backend yet, but prepared)
        // await _audioPlayer.play(UrlSource(response['audio_url']));
      }
    } catch (e) {
      setState(() {
        _responseText = "Error: ${e.toString()}";
        _isLoading = false;
        _statusText = "Tap to retry";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('JanSathi'),
        backgroundColor: Colors.orange,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              if (_responseText.isNotEmpty)
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.orange.shade50,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: Colors.orange.shade200)
                  ),
                  child: Text(
                    _responseText,
                    style: const TextStyle(fontSize: 18),
                    textAlign: TextAlign.center,
                  ),
                ),
              const SizedBox(height: 40),
              GestureDetector(
                onTap: _isLoading ? null : (_isRecording ? _stopRecording : _startRecording),
                child: Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    color: _isLoading ? Colors.grey : (_isRecording ? Colors.red : Colors.blue),
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black26,
                        blurRadius: 10,
                        offset: const Offset(0, 5),
                      )
                    ],
                  ),
                  child: Icon(
                    _isLoading ? Icons.hourglass_bottom : (_isRecording ? Icons.stop : Icons.mic),
                    color: Colors.white,
                    size: 50,
                  ),
                ),
              ),
              const SizedBox(height: 20),
              Text(
                _statusText,
                style: Theme.of(context).textTheme.headlineSmall,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
