import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

class ApiService {
  // IMPORTANT: For local emulator/device, use your machine's IP. 
  // '10.0.2.2' is for Android Emulator to access localhost.
  // If running on a physical device, change this to your laptop's Wi-Fi IP (e.g., 192.168.1.5).
  final String baseUrl = "http://10.0.2.2:5000"; 

  Future<Map<String, dynamic>> sendVoiceQuery(String filePath) async {
    try {
      var uri = Uri.parse('$baseUrl/query');
      var request = http.MultipartRequest('POST', uri);
      
      request.files.add(await http.MultipartFile.fromPath(
        'audio_file',
        filePath,
        contentType: MediaType('audio', 'wav'),
      ));

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        print("Server Error: ${response.body}");
        throw Exception('Failed to get response from JanSathi Brain');
      }
    } catch (e) {
      print("API Error: $e");
      throw Exception('Network Error: Make sure the server is running on the correct IP.');
    }
  }
}
