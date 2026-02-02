import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

class ApiService {
  // Platform-aware base URL
  static String get baseUrl {
    if (kIsWeb) {
      return "http://localhost:5000";
    }
    // Android emulator
    return "http://10.0.2.2:5000";
  }

  /// TEXT QUERY
  /// Matches backend expectation: { "text_query": "..." }
  Future<Map<String, dynamic>> sendTextQuery(String text) async {
    try {
      final uri = Uri.parse('$baseUrl/query');

      final response = await http.post(
        uri,
        headers: const {
          "Content-Type": "application/json",
        },
        body: jsonEncode({
          "text_query": text,
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception(
          "Server error (${response.statusCode}): ${response.body}",
        );
      }
    } catch (e) {
      throw Exception(
        "Network error while contacting JanSathi backend: $e",
      );
    }
  }

  /// VOICE QUERY (Web-safe)
  /// Uploads audio bytes instead of file paths
  Future<Map<String, dynamic>> sendVoiceQuery(List<int> audioBytes) async {
    try {
      final uri = Uri.parse('$baseUrl/query');
      final request = http.MultipartRequest('POST', uri);

      request.files.add(
        http.MultipartFile.fromBytes(
          'audio_file',
          audioBytes,
          filename: 'audio.wav',
          contentType: MediaType('audio', 'wav'),
        ),
      );

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception(
          "Server error (${response.statusCode}): ${response.body}",
        );
      }
    } catch (e) {
      throw Exception(
        "Network error while sending voice query: $e",
      );
    }
  }
}
