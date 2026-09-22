"""Generate the circular north-up radar SVG without rebuilding the island."""
from pathlib import Path
from mountain_profile import height


def render_radar(destination):
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="240" height="274" viewBox="0 0 240 274">',
           '<defs><clipPath id="disc"><circle cx="120" cy="138" r="106"/></clipPath></defs>',
           '<circle cx="120" cy="138" r="118" fill="#102a2b" fill-opacity=".95" stroke="#83b7a5" stroke-width="2"/>',
           '<circle cx="120" cy="138" r="107" fill="#28505a" stroke="#527e70" stroke-width="1"/>',
           '<g clip-path="url(#disc)">']
    colors = ['#365c46', '#4e7350', '#6b8759', '#8b986b', '#a5a68a', '#c4baa0']
    for j in range(100):
        for i in range(100):
            x, y = -6600 + (i+.5)*132, -6900 + (j+.5)*133
            if -6350 < x < 6350 and -6650 < y < 6150:
                color = colors[min(5, int(height(x, y)/500))]
                svg.append(f'<rect x="{41.56+i*1.5688:.4f}" y="{59.56+j*1.5688:.4f}" width="1.59" height="1.59" fill="{color}"/>')
    svg.extend(['<path d="M120 32V244M14 138H226" stroke="#b1cfad" stroke-opacity=".18"/>',
                '<circle cx="120" cy="138" r="53" fill="none" stroke="#b1cfad" stroke-opacity=".12"/></g>',
                '<g fill="#eef4df" font-family="sans-serif" font-size="11" text-anchor="middle"><text x="120" y="31">N</text><text x="120" y="253">S</text><text x="9" y="142">W</text><text x="231" y="142">E</text></g>',
                '<text x="120" y="272" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#d5e7d3">▲ YOU   ◆ CAMP   ● TARGET</text></svg>'])
    Path(destination).write_text(''.join(svg), encoding='utf-8')


if __name__ == '__main__':
    render_radar(Path(__file__).resolve().parents[1] / 'assets/ui/radar-map.svg')
