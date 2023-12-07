from SwimmingDetector import SwimmingDetector


def main():
    # Swimming Detector
    detector = SwimmingDetector()

    detector.count_strokes()

    spm = detector.get_strokes_per_minute()
    sp25 = detector.get_stroke()

    print(f'Strokes Per Minute: {int(spm)}')
    print(f'Strokes Per 25 Meters: {sp25}')

    detector.plot_angles()


if __name__ == "__main__":
    main()
