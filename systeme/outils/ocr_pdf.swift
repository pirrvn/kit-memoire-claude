// Reconnaissance de texte (OCR) d'un PDF scanné, avec les outils intégrés à macOS (PDFKit et Vision), sans installation.
// Usage : swift systeme/outils/ocr_pdf.swift sources/pdf/Fichier.pdf > sources/pdf/Fichier.txt
import Foundation
import PDFKit
import Vision
import AppKit

let args = CommandLine.arguments
guard args.count > 1, let doc = PDFDocument(url: URL(fileURLWithPath: args[1])) else {
    FileHandle.standardError.write("Usage : swift ocr_pdf.swift fichier.pdf\n".data(using: .utf8)!)
    exit(1)
}
for i in 0..<doc.pageCount {
    guard let page = doc.page(at: i) else { continue }
    let box = page.bounds(for: .mediaBox)
    let scale: CGFloat = 3.0
    let size = NSSize(width: box.width * scale, height: box.height * scale)
    let image = page.thumbnail(of: size, for: .mediaBox)
    var rect = NSRect(origin: .zero, size: image.size)
    guard let cg = image.cgImage(forProposedRect: &rect, context: nil, hints: nil) else { continue }
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["en-US", "fr-FR"]
    request.usesLanguageCorrection = true
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([request])
    print("\n=== PAGE PDF \(i + 1)")
    for obs in (request.results ?? []) {
        if let best = obs.topCandidates(1).first { print(best.string) }
    }
}
