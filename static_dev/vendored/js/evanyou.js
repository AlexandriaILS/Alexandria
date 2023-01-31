/*The MIT License (MIT)

Copyright (c) EGOIST <0x142857@gmail.com> (github.com/egoist)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Modifications by Joe Kaufeld (github.com/itsthejoker) */

// usage:
//   <script src="{% static 'vendored/js/evanyou.js' %}" defer></script>
//   <canvas id="evanyou-canvas"></canvas>

'use strict';

var evanyou = function () {
    var c = document.getElementById('evanyou-canvas'),
        x = c.getContext('2d'),
        pr = window.devicePixelRatio || 1,
        w = window.innerWidth,
        h = window.innerHeight,
        f = 90,
        q,
        m = Math,
        r = 0,
        u = m.PI * 2,
        v = m.cos,
        z = m.random;
    c.width = w * pr;
    c.height = h * pr;
    x.scale(pr, pr);
    x.globalAlpha = 0.6;

    function i() {
        x.clearRect(0, 0, w, h);
        q = [{x: 0, y: h * .7 + f}, {x: 0, y: h * .7 - f}];
        while (q[1].x < w + f) {
            d(q[0], q[1]);
        }
    }

    function d(i, j) {
        function hexToRgb(h) {
            return ['0x' + h[1] + h[2] | 0, '0x' + h[3] + h[4] | 0, '0x' + h[5] + h[6] | 0]
        }

        x.beginPath();
        x.moveTo(i.x, i.y);
        x.lineTo(j.x, j.y);
        var k = j.x + (z() * 2 - 0.25) * f,
            n = y(j.y);
        x.lineTo(k, n);
        x.closePath();
        r -= u / -50;
        x.fillStyle = `rgb(${hexToRgb('#' + (v(r) * 127 + 128 << 16 | v(r + u / 3) * 127 + 128 << 8 | v(r + u / 3 * 2) * 127 + 128).toString(16))})`;
        x.fill();
        q[0] = q[1];
        q[1] = {x: k, y: n};
    }

    function y(p) {
        var t = p + (z() * 2 - 1.1) * f;
        return (t > h || t < 0) ? y(p) : t
    }

    i();
    return i
};

document.addEventListener("DOMContentLoaded", function (event) {
    var canvas = document.createElement('canvas');
    canvas.id = 'evanyou-canvas';
    canvas.style.position = 'absolute';
    canvas.style.top = 0;
    canvas.style.left = 0;
    canvas.style.zIndex = -2000;
    canvas.style.width = '100%';
    canvas.style.width = '100%';
    canvas.style.pointerEvents = 'none';
    document.body.appendChild(canvas);
    document.body.addEventListener('click', evanyou());
})
