#!/usr/bin/env swift

import CoreImage
import CoreImage.CIFilterBuiltins
import Foundation
import ImageIO
import UniformTypeIdentifiers
import Vision

enum CutoutError: Error, CustomStringConvertible {
    case usage
    case unreadableImage(String)
    case noForeground
    case renderFailed
    case writeFailed(String)

    var description: String {
        switch self {
        case .usage:
            return "usage: remove_background.swift INPUT OUTPUT.png"
        case .unreadableImage(let path):
            return "unable to read image: \(path)"
        case .noForeground:
            return "no foreground instance detected"
        case .renderFailed:
            return "unable to render transparent cutout"
        case .writeFailed(let path):
            return "unable to write PNG: \(path)"
        }
    }
}

func loadCGImage(_ path: String) throws -> CGImage {
    let url = URL(fileURLWithPath: path) as CFURL
    guard let source = CGImageSourceCreateWithURL(url, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        throw CutoutError.unreadableImage(path)
    }
    return image
}

func writePNG(_ image: CGImage, to path: String) throws {
    let url = URL(fileURLWithPath: path) as CFURL
    guard let destination = CGImageDestinationCreateWithURL(
        url, UTType.png.identifier as CFString, 1, nil
    ) else {
        throw CutoutError.writeFailed(path)
    }
    CGImageDestinationAddImage(destination, image, nil)
    guard CGImageDestinationFinalize(destination) else {
        throw CutoutError.writeFailed(path)
    }
}

do {
    guard CommandLine.arguments.count == 3 else { throw CutoutError.usage }
    let inputPath = CommandLine.arguments[1]
    let outputPath = CommandLine.arguments[2]
    let sourceImage = try loadCGImage(inputPath)

    let handler = VNImageRequestHandler(cgImage: sourceImage, options: [:])
    let request = VNGenerateForegroundInstanceMaskRequest()
    try handler.perform([request])
    guard let observation = request.results?.first else {
        throw CutoutError.noForeground
    }

    let maskBuffer = try observation.generateScaledMaskForImage(
        forInstances: observation.allInstances,
        from: handler
    )
    let foreground = CIImage(cgImage: sourceImage)
    let mask = CIImage(cvPixelBuffer: maskBuffer)
    let transparent = CIImage(color: .clear).cropped(to: foreground.extent)
    let blend = CIFilter.blendWithMask()
    blend.inputImage = foreground
    blend.backgroundImage = transparent
    blend.maskImage = mask

    let context = CIContext(options: [.useSoftwareRenderer: false])
    guard let result = blend.outputImage,
          let cgResult = context.createCGImage(result, from: foreground.extent) else {
        throw CutoutError.renderFailed
    }
    try writePNG(cgResult, to: outputPath)
    print(outputPath)
} catch {
    fputs("\(error)\n", stderr)
    exit(1)
}
