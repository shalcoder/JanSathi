class OfflineService {
  // Static Cache of Critical Information (English + Hindi Support)
  final Map<String, String> _faqCache = {
    "pm kisan": "PM Kisan Samman Nidhi provides ₹6,000 per year to farmers. Visit pmkisan.gov.in. (Offline Mode)",
    "ration card": "For Ration Card output, please visit your nearest PDS shop or State Food Portal. (Offline Mode)",
    "scholarship": "National Scholarship Portal (scholarships.gov.in) is open for applications. (Offline Mode)",
    "health": "Ayushman Bharat provides ₹5 Lakh health cover. Call 14555. (Offline Mode)",
    "फसल": "PM Fasal Bima Yojana provides crop insurance. Contact your bank. (Offline Mode)", // 'Crop' in Hindi
    "kisan credit card": "KCC offers low-interest loans to farmers. Apply at any localized bank branch. (Offline Mode)",
  };

  // Simple Keyword Matcher
  String? search(String query) {
    if (query.trim().isEmpty) return null;
    
    final lowerQuery = query.toLowerCase();
    
    for (var key in _faqCache.keys) {
      if (lowerQuery.contains(key)) {
        return _faqCache[key];
      }
    }
    
    return null; // No match found
  }
}
