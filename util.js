"use strict";

/* --------------------================-------------------- */
/*                    Utility  Functions                    */
/* --------------------================-------------------- */

function $(selector) {
	return document.querySelector(selector);
}

function $$(selector) {
	return [].slice.call(document.querySelectorAll(selector));
}

let h, svg;
(function() {
	function _generateElement(args, el) {
		let e = null;
		let _tci = args.shift().split(/\s*(?=[.#])/); // tag, class, id
		if(/[.#]/.test(_tci[0])) e = el('div');
		_tci.forEach(function(v) {
			if(!e) e = el(v);
			else if(v[0] === '.') e.classList.add(v.slice(1));
			else if(v[0] === '#') e.setAttribute('id', v.slice(1));
		});
		function item(l) {
			switch (l.constructor) {
				case Array:
					l.forEach(item);
					break;
				case Object:
					for(let attr in l) {
						if(attr === 'style') {
							for(let style in l[attr]) {
								e.style[style] = l[attr][style];
							}
						}else if(attr.substr(0, 2) === 'on'){
							e.addEventListener(attr.substr(2), l[attr]);
						}else{
							e.setAttribute(attr, l[attr]);
						}
					}
					break;
				default:
					if(l.nodeType != undefined) e.appendChild(l)
    				else e.appendChild(document.createTextNode(l))
			}
		}
		while(args.length > 0) {
			item(args.shift());
		}
		return e;
	}

	h = function() {
		return _generateElement([].slice.call(arguments), function(tagName) {
			return document.createElement(tagName);
		});
	}

	svg = function() {
		return _generateElement([].slice.call(arguments), function(tagName) {
			return document.createElementNS('http://www.w3.org/2000/svg', tagName);
		});
	}
})(); // h, svg


let random = {
	int: function(a, b) {
		return Math.floor(Math.random() * (b - a + 1) + a);
	},
	choice: function(A) {
		return A[random.int(0, A.length - 1)];
	},
	gaussian: function(mean, stdev) {
		var samples = 6;
		
		var rand = 0;
		for (var i = 0; i < samples; i += 1) {
			rand += Math.random() - 0.5;
		}
		rand = rand / 6;

		return mean + rand * stdev * 2;
	}
}