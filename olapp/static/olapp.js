/* ═══════════════════════════════════════════════════════════════════════
   OLAPP — Frontend Application
   ═══════════════════════════════════════════════════════════════════════ */
(() => {
    'use strict';

    const state = { config: null, values: {}, loading: false, theme: 'light', sse: null };

    // ─── Helpers ──────────────────────────────────────────────────────
    const $ = (sel, ctx = document) => ctx.querySelector(sel);
    const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

    function el(tag, attrs = {}, children = []) {
        const node = document.createElement(tag);
        for (const [k, v] of Object.entries(attrs)) {
            if (k === 'className') node.className = v;
            else if (k === 'innerHTML') node.innerHTML = v;
            else if (k === 'textContent') node.textContent = v;
            else if (k.startsWith('on')) node.addEventListener(k.slice(2).toLowerCase(), v);
            else if (k === 'style' && typeof v === 'object') Object.assign(node.style, v);
            else if (k === 'dataset') Object.assign(node.dataset, v);
            else node.setAttribute(k, v);
        }
        for (const c of (Array.isArray(children) ? children : [children])) {
            if (typeof c === 'string') node.appendChild(document.createTextNode(c));
            else if (c instanceof Node) node.appendChild(c);
        }
        return node;
    }

    // ─── Toast ────────────────────────────────────────────────────────
    function toast(message, type = 'info', title = '', duration = 4000) {
        const icons = { error: '✕', success: '✓', warning: '!', info: 'i' };
        const t = el('div', { className: `olapp-toast ${type}` }, [
            el('span', { className: 'olapp-toast-icon', textContent: icons[type] || icons.info }),
            el('div', { className: 'olapp-toast-content' }, [
                title ? el('div', { className: 'olapp-toast-title', textContent: title }) : null,
                el('div', { className: 'olapp-toast-message', textContent: message }),
            ].filter(Boolean)),
            el('button', { className: 'olapp-toast-close', textContent: '×', onClick: () => dismiss(t) }),
        ]);
        const container = $('#olapp-toast-container');
        container.appendChild(t);
        setTimeout(() => dismiss(t), duration);
    }

    function dismiss(t) {
        t.classList.add('removing');
        setTimeout(() => t.remove(), 250);
    }

    // ─── API ──────────────────────────────────────────────────────────
    async function api(method, url, data) {
        const opts = { method, headers: {} };
        if (data) {
            opts.headers['Content-Type'] = 'application/json';
            opts.body = JSON.stringify(data);
        }
        const res = await fetch(url, opts);
        const json = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(json.error || `HTTP ${res.status}`);
        return json;
    }

    // ─── Component Renderers ──────────────────────────────────────────
    const renderers = {
        textbox(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const multiline = (cfg.lines || 1) > 1;
            const input = multiline
                ? el('textarea', { className: 'olapp-textarea', placeholder: cfg.placeholder || '', rows: cfg.lines || 3, dataset: { id: cfg.id } })
                : el('input', { className: 'olapp-input', type: 'text', placeholder: cfg.placeholder || '', dataset: { id: cfg.id } });
            if (cfg.value) input.value = cfg.value;
            state.values[cfg.id] = cfg.value || '';
            input.addEventListener('input', () => { state.values[cfg.id] = input.value; });
            wrap.appendChild(input);
            container.appendChild(wrap);
        },

        number(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const group = el('div', { className: 'olapp-number-group' });
            const input = el('input', { className: 'olapp-input', type: 'number', step: cfg.step || 1, dataset: { id: cfg.id } });
            if (cfg.minimum != null) input.min = cfg.minimum;
            if (cfg.maximum != null) input.max = cfg.maximum;
            if (cfg.value != null) input.value = cfg.value;
            state.values[cfg.id] = cfg.value ?? '';
            const minus = el('button', { className: 'olapp-number-btn', textContent: '−', onClick: () => { input.stepDown(); input.dispatchEvent(new Event('input')); } });
            const plus = el('button', { className: 'olapp-number-btn', textContent: '+', onClick: () => { input.stepUp(); input.dispatchEvent(new Event('input')); } });
            input.addEventListener('input', () => { state.values[cfg.id] = input.value === '' ? '' : Number(input.value); });
            group.append(minus, input, plus);
            wrap.appendChild(group);
            container.appendChild(wrap);
        },

        slider(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const row = el('div', { className: 'olapp-slider-container' });
            const slider = el('input', { className: 'olapp-slider', type: 'range', min: cfg.minimum ?? 0, max: cfg.maximum ?? 100, step: cfg.step || 1, value: cfg.value ?? cfg.minimum ?? 0, dataset: { id: cfg.id } });
            const val = el('span', { className: 'olapp-slider-value', textContent: slider.value });
            state.values[cfg.id] = Number(slider.value);
            slider.addEventListener('input', () => { val.textContent = slider.value; state.values[cfg.id] = Number(slider.value); });
            row.append(slider, val);
            wrap.appendChild(row);
            container.appendChild(wrap);
        },

        checkbox(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            const group = el('label', { className: 'olapp-checkbox-group' });
            const cb = el('input', { className: 'olapp-checkbox', type: 'checkbox', dataset: { id: cfg.id } });
            if (cfg.value) cb.checked = true;
            state.values[cfg.id] = !!cfg.value;
            cb.addEventListener('change', () => { state.values[cfg.id] = cb.checked; });
            group.append(cb, el('span', { textContent: cfg.label || '' }));
            wrap.appendChild(group);
            container.appendChild(wrap);
        },

        dropdown(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const sel = el('select', { className: 'olapp-select', dataset: { id: cfg.id } });
            for (const choice of (cfg.choices || [])) {
                const opt = el('option', { value: choice, textContent: choice });
                if (choice === cfg.value) opt.selected = true;
                sel.appendChild(opt);
            }
            state.values[cfg.id] = cfg.value || (cfg.choices || [])[0] || '';
            sel.addEventListener('change', () => { state.values[cfg.id] = sel.value; });
            wrap.appendChild(sel);
            container.appendChild(wrap);
        },

        radio(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const group = el('div', { className: 'olapp-radio-group' });
            state.values[cfg.id] = cfg.value || (cfg.choices || [])[0] || '';
            for (const choice of (cfg.choices || [])) {
                const opt = el('label', { className: `olapp-radio-option${choice === state.values[cfg.id] ? ' active' : ''}` });
                const radio = el('input', { className: 'olapp-radio', type: 'radio', name: cfg.id, value: choice, dataset: { id: cfg.id } });
                if (choice === state.values[cfg.id]) radio.checked = true;
                radio.addEventListener('change', () => {
                    state.values[cfg.id] = choice;
                    $$('.olapp-radio-option', group).forEach(o => o.classList.remove('active'));
                    opt.classList.add('active');
                });
                opt.append(radio, el('span', { textContent: choice }));
                group.appendChild(opt);
            }
            wrap.appendChild(group);
            container.appendChild(wrap);
        },

        button(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            const btn = el('button', { className: `olapp-btn olapp-btn-${cfg.variant || 'primary'}`, textContent: cfg.label || cfg.value || 'Button', dataset: { id: cfg.id } });
            state.values[cfg.id] = cfg.value || cfg.label;
            wrap.appendChild(btn);
            container.appendChild(wrap);
        },

        image(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const box = el('div', { className: 'olapp-image-container', dataset: { id: cfg.id } });
            const fileInput = el('input', { type: 'file', accept: 'image/*', style: { display: 'none' } });
            const placeholder = el('div', { style: { textAlign: 'center' } }, [
                el('div', { className: 'olapp-image-placeholder-icon', textContent: '↑' }),
                el('div', { className: 'olapp-image-placeholder-text', textContent: 'Click to upload or drag image here' }),
                el('div', { className: 'olapp-image-placeholder-hint', textContent: 'PNG, JPG, GIF, WebP' }),
            ]);
            box.append(placeholder, fileInput);
            state.values[cfg.id] = cfg.value || null;
            if (cfg.value) {
                const img = el('img', { src: cfg.value });
                box.innerHTML = '';
                box.appendChild(img);
                box.classList.add('has-image');
            }
            box.addEventListener('click', () => fileInput.click());
            fileInput.addEventListener('change', () => {
                const file = fileInput.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = (e) => {
                    state.values[cfg.id] = e.target.result;
                    box.innerHTML = '';
                    box.appendChild(el('img', { src: e.target.result }));
                    box.classList.add('has-image');
                };
                reader.readAsDataURL(file);
            });
            box.addEventListener('dragover', (e) => { e.preventDefault(); box.style.borderColor = 'var(--olapp-primary)'; });
            box.addEventListener('dragleave', () => { box.style.borderColor = ''; });
            box.addEventListener('drop', (e) => {
                e.preventDefault(); box.style.borderColor = '';
                const file = e.dataTransfer.files[0];
                if (file && file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = (ev) => {
                        state.values[cfg.id] = ev.target.result;
                        box.innerHTML = '';
                        box.appendChild(el('img', { src: ev.target.result }));
                        box.classList.add('has-image');
                    };
                    reader.readAsDataURL(file);
                }
            });
            wrap.appendChild(box);
            container.appendChild(wrap);
        },

        audio(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const box = el('div', { className: 'olapp-audio-container', dataset: { id: cfg.id } });
            const fileInput = el('input', { type: 'file', accept: 'audio/*', style: { display: 'none' } });
            const btn = el('button', { className: 'olapp-btn olapp-btn-secondary', textContent: 'Upload Audio' });
            state.values[cfg.id] = cfg.value || null;
            if (cfg.value) box.appendChild(el('audio', { controls: true, src: cfg.value }));
            box.append(btn, fileInput);
            btn.addEventListener('click', () => fileInput.click());
            fileInput.addEventListener('change', () => {
                const file = fileInput.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = (e) => {
                    state.values[cfg.id] = e.target.result;
                    box.innerHTML = '';
                    box.appendChild(el('audio', { controls: true, src: e.target.result }));
                };
                reader.readAsDataURL(file);
            });
            wrap.appendChild(box);
            container.appendChild(wrap);
        },

        video(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const box = el('div', { className: 'olapp-video-container', dataset: { id: cfg.id } });
            const fileInput = el('input', { type: 'file', accept: 'video/*', style: { display: 'none' } });
            const btn = el('button', { className: 'olapp-btn olapp-btn-secondary', textContent: 'Upload Video' });
            state.values[cfg.id] = cfg.value || null;
            if (cfg.value) box.appendChild(el('video', { controls: true, src: cfg.value, style: { maxWidth: '100%' } }));
            box.append(btn, fileInput);
            btn.addEventListener('click', () => fileInput.click());
            fileInput.addEventListener('change', () => {
                const file = fileInput.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = (e) => {
                    state.values[cfg.id] = e.target.result;
                    box.innerHTML = '';
                    box.appendChild(el('video', { controls: true, src: e.target.result, style: { maxWidth: '100%' } }));
                };
                reader.readAsDataURL(file);
            });
            wrap.appendChild(box);
            container.appendChild(wrap);
        },

        file(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const box = el('div', { className: 'olapp-file-container', dataset: { id: cfg.id } });
            const fileInput = el('input', { type: 'file', style: { display: 'none' } });
            if (cfg.file_types?.length) fileInput.accept = cfg.file_types.join(',');
            const content = el('div', { style: { textAlign: 'center' } }, [
                el('div', { textContent: '↑', style: { fontSize: '1.5rem', color: 'var(--olapp-text-muted)', marginBottom: '4px' } }),
                el('div', { textContent: 'Click to upload file', style: { color: 'var(--olapp-text-muted)', fontSize: 'var(--olapp-text-sm)' } }),
            ]);
            box.append(content, fileInput);
            state.values[cfg.id] = null;
            box.addEventListener('click', () => fileInput.click());
            fileInput.addEventListener('change', () => {
                const file = fileInput.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = (e) => {
                    state.values[cfg.id] = e.target.result;
                    content.innerHTML = '';
                    content.appendChild(el('div', { textContent: file.name, style: { fontWeight: '500' } }));
                };
                reader.readAsDataURL(file);
            });
            wrap.appendChild(box);
            container.appendChild(wrap);
        },

        dataframe(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const data = cfg.value || { headers: cfg.headers || [], data: [] };
            const wrapper = el('div', { className: 'olapp-dataframe-wrapper' });
            const table = el('table', { className: 'olapp-dataframe', dataset: { id: cfg.id } });
            const thead = el('thead');
            const tbody = el('tbody');
            const headers = data.headers || cfg.headers || [];
            const rows = data.data || [];
            if (headers.length) {
                const tr = el('tr');
                headers.forEach(h => tr.appendChild(el('th', { textContent: h })));
                thead.appendChild(tr);
            }
            rows.forEach(row => {
                const tr = el('tr');
                row.forEach(cell => tr.appendChild(el('td', { textContent: String(cell ?? '') })));
                tbody.appendChild(tr);
            });
            table.append(thead, tbody);
            wrapper.appendChild(table);
            state.values[cfg.id] = data;
            wrap.appendChild(wrapper);
            container.appendChild(wrap);
        },

        markdown(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            const md = el('div', { className: 'olapp-markdown', innerHTML: mdRender(cfg.value || ''), dataset: { id: cfg.id } });
            state.values[cfg.id] = cfg.value || '';
            wrap.appendChild(md);
            container.appendChild(wrap);
        },

        html(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            const html = el('div', { innerHTML: cfg.value || '', dataset: { id: cfg.id } });
            state.values[cfg.id] = cfg.value || '';
            wrap.appendChild(html);
            container.appendChild(wrap);
        },

        chatbot(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const chatbot = el('div', { className: 'olapp-chatbot', dataset: { id: cfg.id } });
            const msgs = el('div', { className: 'olapp-chatbot-messages' });
            const inputRow = el('div', { className: 'olapp-chatbot-input' });
            const input = el('input', { className: 'olapp-input', type: 'text', placeholder: cfg.placeholder || 'Type a message...' });
            const sendBtn = el('button', { className: 'olapp-btn olapp-btn-primary', textContent: 'Send' });
            state.values[cfg.id] = cfg.value || [];

            function renderMsgs(messages) {
                msgs.innerHTML = '';
                for (const [user, bot] of (messages || [])) {
                    if (user != null) msgs.appendChild(chatMsg('user', user));
                    if (bot != null) msgs.appendChild(chatMsg('bot', bot));
                }
                msgs.scrollTop = msgs.scrollHeight;
            }

            function chatMsg(role, text) {
                return el('div', { className: `olapp-chat-message ${role}` }, [
                    el('div', { className: 'olapp-chat-avatar', textContent: role === 'user' ? 'U' : 'A' }),
                    el('div', { className: 'olapp-chat-bubble', textContent: text }),
                ]);
            }

            renderMsgs(cfg.value);
            inputRow.append(input, sendBtn);
            chatbot.append(msgs, inputRow);
            wrap.appendChild(chatbot);
            container.appendChild(wrap);
        },

        state(cfg) {
            state.values[cfg.id] = cfg.value;
        },

        colorpicker(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const row = el('div', { style: { display: 'flex', alignItems: 'center', gap: '12px' } });
            const input = el('input', { type: 'color', value: cfg.value || '#6366f1', dataset: { id: cfg.id }, style: { width: '48px', height: '36px', border: 'var(--olapp-border)', borderRadius: 'var(--olapp-radius)', cursor: 'pointer', padding: '2px' } });
            const hex = el('input', { className: 'olapp-input', type: 'text', value: cfg.value || '#6366f1', style: { width: '100px', fontFamily: 'var(--olapp-mono)', fontSize: 'var(--olapp-text-sm)' } });
            state.values[cfg.id] = cfg.value || '#6366f1';
            input.addEventListener('input', () => { hex.value = input.value; state.values[cfg.id] = input.value; });
            hex.addEventListener('change', () => { input.value = hex.value; state.values[cfg.id] = hex.value; });
            row.append(input, hex);
            wrap.appendChild(row);
            container.appendChild(wrap);
        },

        datetime(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const input = el('input', { className: 'olapp-input', type: cfg.include_time !== false ? 'datetime-local' : 'date', dataset: { id: cfg.id } });
            if (cfg.value) input.value = cfg.value;
            state.values[cfg.id] = cfg.value || '';
            input.addEventListener('input', () => { state.values[cfg.id] = input.value; });
            wrap.appendChild(input);
            container.appendChild(wrap);
        },

        code(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const textarea = el('textarea', { className: 'olapp-textarea', placeholder: cfg.placeholder || 'Enter code...', rows: cfg.lines || 10, dataset: { id: cfg.id }, style: { fontFamily: 'var(--olapp-mono)', fontSize: 'var(--olapp-text-sm)', tabSize: '4', whiteSpace: 'pre', overflowX: 'auto' } });
            if (cfg.value) textarea.value = cfg.value;
            state.values[cfg.id] = cfg.value || '';
            textarea.addEventListener('input', () => { state.values[cfg.id] = textarea.value; });
            textarea.addEventListener('keydown', (e) => { if (e.key === 'Tab') { e.preventDefault(); const s = textarea.selectionStart, end = textarea.selectionEnd; textarea.value = textarea.value.substring(0, s) + '    ' + textarea.value.substring(end); textarea.selectionStart = textarea.selectionEnd = s + 4; textarea.dispatchEvent(new Event('input')); } });
            wrap.appendChild(textarea);
            container.appendChild(wrap);
        },

        gallery(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const grid = el('div', { style: { display: 'grid', gridTemplateColumns: `repeat(${cfg.columns || 3}, 1fr)`, gap: '8px' }, dataset: { id: cfg.id } });
            state.values[cfg.id] = cfg.value || [];
            for (const src of (cfg.value || [])) {
                const item = el('div', { style: { aspectRatio: '1', overflow: 'hidden', borderRadius: 'var(--olapp-radius)', border: 'var(--olapp-border)' } });
                item.appendChild(el('img', { src, style: { width: '100%', height: '100%', objectFit: 'cover' } }));
                grid.appendChild(item);
            }
            if (!(cfg.value || []).length) {
                grid.appendChild(el('div', { textContent: 'No images', style: { gridColumn: '1 / -1', textAlign: 'center', padding: '24px', color: 'var(--olapp-text-muted)' } }));
            }
            wrap.appendChild(grid);
            container.appendChild(wrap);
        },

        label(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const box = el('div', { dataset: { id: cfg.id } });
            state.values[cfg.id] = cfg.value || {};
            const data = cfg.value || {};
            const sorted = Object.entries(data).sort((a, b) => b[1] - a[1]);
            for (const [name, conf] of sorted.slice(0, cfg.num_top_classes || 5)) {
                const row = el('div', { style: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' } });
                const bar = el('div', { style: { flex: '1', height: '6px', background: 'var(--olapp-gray-200)', borderRadius: '3px', overflow: 'hidden' } });
                bar.appendChild(el('div', { style: { width: `${(conf * 100).toFixed(1)}%`, height: '100%', background: 'var(--olapp-primary)', borderRadius: '3px', transition: 'width 0.3s' } }));
                row.append(el('span', { textContent: name, style: { minWidth: '80px', fontSize: 'var(--olapp-text-sm)', fontWeight: '500' } }), bar, el('span', { textContent: `${(conf * 100).toFixed(1)}%`, style: { minWidth: '48px', textAlign: 'right', fontSize: 'var(--olapp-text-sm)', color: 'var(--olapp-text-secondary)', fontFamily: 'var(--olapp-mono)' } }));
                box.appendChild(row);
            }
            wrap.appendChild(box);
            container.appendChild(wrap);
        },

        highlightedtext(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const box = el('div', { dataset: { id: cfg.id }, style: { lineHeight: '1.8', padding: '12px', background: 'var(--olapp-bg-secondary)', border: 'var(--olapp-border)', borderRadius: 'var(--olapp-radius)' } });
            state.values[cfg.id] = cfg.value || [];
            const colors = ['#fbbf24', '#34d399', '#60a5fa', '#f472b6', '#a78bfa', '#fb923c'];
            const cats = {};
            let ci = 0;
            for (const [text, cat] of (cfg.value || [])) {
                if (cat && !cats[cat]) { cats[cat] = colors[ci % colors.length]; ci++; }
                const span = el('span', { textContent: text });
                if (cat) { span.style.background = cats[cat] + '33'; span.style.borderBottom = `2px solid ${cats[cat]}`; span.style.padding = '1px 2px'; span.style.borderRadius = '2px'; span.title = cat; }
                box.appendChild(span);
            }
            wrap.appendChild(box);
            container.appendChild(wrap);
        },

        json(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const pre = el('pre', { dataset: { id: cfg.id }, style: { background: 'var(--olapp-bg-secondary)', border: 'var(--olapp-border)', borderRadius: 'var(--olapp-radius)', padding: '12px', fontFamily: 'var(--olapp-mono)', fontSize: 'var(--olapp-text-sm)', overflow: 'auto', maxHeight: '300px', whiteSpace: 'pre-wrap' } });
            try { pre.textContent = JSON.stringify(cfg.value ?? {}, null, 2); } catch { pre.textContent = String(cfg.value); }
            state.values[cfg.id] = cfg.value || {};
            wrap.appendChild(pre);
            container.appendChild(wrap);
        },

        progress(cfg, container) {
            const wrap = el('div', { className: 'olapp-component' });
            if (cfg.label) wrap.appendChild(el('label', { className: 'olapp-label', textContent: cfg.label }));
            const bar = el('div', { dataset: { id: cfg.id }, style: { height: '8px', background: 'var(--olapp-gray-200)', borderRadius: '4px', overflow: 'hidden' } });
            const fill = el('div', { style: { width: `${((cfg.value || 0) * 100).toFixed(0)}%`, height: '100%', background: 'var(--olapp-primary)', borderRadius: '4px', transition: 'width 0.3s' } });
            state.values[cfg.id] = cfg.value || 0;
            bar.appendChild(fill);
            wrap.appendChild(bar);
            container.appendChild(wrap);
        },
    };

    // ─── Markdown (minimal) ───────────────────────────────────────────
    function mdRender(text) {
        if (!text) return '';
        return text
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/^### (.+)$/gm, '<h3>$1</h3>')
            .replace(/^## (.+)$/gm, '<h2>$1</h2>')
            .replace(/^# (.+)$/gm, '<h1>$1</h1>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/^[-*] (.+)$/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
            .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
    }

    // ─── Layout Renderer ──────────────────────────────────────────────
    function renderLayout(items, container) {
        for (const item of items) {
            if (!item) continue;
            if (item.type === 'row') {
                const row = el('div', { className: 'olapp-block row' });
                renderLayout(item.children || [], row);
                container.appendChild(row);
            } else if (item.type === 'column') {
                const col = el('div', { className: 'olapp-block column' });
                if (item.scale) col.style.flex = item.scale;
                renderLayout(item.children || [], col);
                container.appendChild(col);
            } else if (item.type === 'group') {
                const group = el('div', { className: 'olapp-block group' });
                renderLayout(item.children || [], group);
                container.appendChild(group);
            } else if (item.type === 'tabs') {
                const tabs = el('div', { className: 'olapp-block' });
                const nav = el('div', { className: 'olapp-tabs-nav' });
                const panels = el('div', {});
                const children = item.children || [];
                children.forEach((tab, i) => {
                    const btn = el('button', { className: `olapp-tab-btn${i === 0 ? ' active' : ''}`, textContent: tab.label || `Tab ${i + 1}` });
                    const panel = el('div', { style: { display: i === 0 ? 'block' : 'none' } });
                    renderLayout(tab.children || [], panel);
                    btn.addEventListener('click', () => {
                        $$('.olapp-tab-btn', nav).forEach(b => b.classList.remove('active'));
                        btn.classList.add('active');
                        $$('.olapp-tab-panel', panels).forEach(p => p.style.display = 'none');
                        panel.style.display = 'block';
                    });
                    panel.className = 'olapp-tab-panel';
                    nav.appendChild(btn);
                    panels.appendChild(panel);
                });
                tabs.append(nav, panels);
                container.appendChild(tabs);
            } else if (item.type === 'accordion') {
                const acc = el('div', { className: `olapp-accordion${item.open ? ' open' : ''}` });
                const header = el('div', { className: 'olapp-accordion-header' }, [
                    el('span', { textContent: item.label || 'Section' }),
                    el('span', { className: 'olapp-accordion-arrow', textContent: '▼' }),
                ]);
                const body = el('div', { className: 'olapp-accordion-body' });
                renderLayout(item.children || [], body);
                header.addEventListener('click', () => acc.classList.toggle('open'));
                acc.append(header, body);
                container.appendChild(acc);
            } else if (renderers[item.type]) {
                renderers[item.type](item, container);
            }
        }
    }

    // ─── SSE ──────────────────────────────────────────────────────────
    function connectSSE() {
        if (state.sse) state.sse.close();
        const src = new EventSource('/api/queue/join');
        state.sse = src;
        src.onmessage = (e) => {
            try {
                const data = JSON.parse(e.data);
                if (data.connected) return;
                if (data.completed && data.output) {
                    updateOutputs(data.output);
                    setLoading(false);
                }
            } catch {}
        };
        src.onerror = () => { setTimeout(connectSSE, 3000); };
    }

    // ─── Predict ──────────────────────────────────────────────────────
    async function predict(apiName = 'predict') {
        if (state.loading) return;
        setLoading(true);
        try {
            const inputValues = [];
            for (const comp of (state.config?.components?.inputs || [])) {
                inputValues.push(state.values[comp.id] ?? comp.value ?? null);
            }
            const result = await api('POST', `/api/${apiName}`, { data: inputValues });
            if (result.data) updateOutputs(result.data);
        } catch (err) {
            toast(err.message, 'error', 'Error');
        } finally {
            setLoading(false);
        }
    }

    function updateOutputs(outputData) {
        const outputs = state.config?.components?.outputs || [];
        const values = Array.isArray(outputData) ? outputData : [outputData];
        const container = $('#olapp-outputs');
        if (!container) return;
        container.innerHTML = '';
        for (let i = 0; i < outputs.length; i++) {
            renderers[outputs[i].type]({ ...outputs[i], value: values[i] ?? outputs[i].value }, container);
        }
    }

    function setLoading(on) {
        state.loading = on;
        const btn = $('#olapp-submit');
        if (!btn) return;
        const text = $('.btn-text', btn);
        const spin = $('.btn-spinner', btn);
        btn.disabled = on;
        if (text) text.style.display = on ? 'none' : '';
        if (spin) spin.style.display = on ? 'inline-flex' : 'none';
    }

    function clearInputs() {
        for (const comp of (state.config?.components?.inputs || [])) {
            state.values[comp.id] = comp.value ?? '';
            const node = $(`[data-id="${comp.id}"]`);
            if (!node) continue;
            if (node.tagName === 'INPUT' || node.tagName === 'TEXTAREA' || node.tagName === 'SELECT') {
                node.value = comp.value ?? '';
            } else if (node.classList.contains('olapp-checkbox')) {
                node.checked = !!comp.value;
            } else if (node.classList.contains('olapp-slider')) {
                node.value = comp.value ?? comp.minimum ?? 0;
                const vd = node.parentElement?.querySelector('.olapp-slider-value');
                if (vd) vd.textContent = node.value;
            }
        }
    }

    // ─── Theme ────────────────────────────────────────────────────────
    function toggleTheme() {
        const html = document.documentElement;
        const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', next);
        state.theme = next;
        const icon = $('.theme-icon', $('#theme-toggle'));
        if (icon) icon.textContent = next === 'dark' ? '🌙' : '☀️';
        localStorage.setItem('olapp-theme', next);
    }

    // ─── Init ─────────────────────────────────────────────────────────
    async function init() {
        const saved = localStorage.getItem('olapp-theme');
        if (saved) {
            document.documentElement.setAttribute('data-theme', saved);
            state.theme = saved;
            const icon = $('.theme-icon', $('#theme-toggle'));
            if (icon) icon.textContent = saved === 'dark' ? '🌙' : '☀️';
        }

        const themeBtn = $('#theme-toggle');
        if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

        try {
            const config = await api('GET', '/api/config');
            state.config = config;

            const loading = $('#olapp-loading');
            if (loading) loading.style.display = 'none';

            if (config.title) {
                document.title = config.title;
                const ts = $('#olapp-title-section');
                const te = $('#olapp-title');
                const de = $('#olapp-description');
                if (te) te.textContent = config.title;
                if (config.description && de) de.textContent = config.description;
                if (ts) ts.style.display = 'block';
            }

            if (config.mode === 'interface') {
                const iface = $('#olapp-interface');
                if (iface) iface.style.display = 'grid';
                const ic = $('#olapp-inputs');
                const oc = $('#olapp-outputs');
                if (ic) { ic.innerHTML = ''; for (const c of (config.components?.inputs || [])) renderers[c.type](c, ic); }
                if (oc) { oc.innerHTML = ''; for (const c of (config.components?.outputs || [])) renderers[c.type](c, oc); }
                const submitBtn = $('#olapp-submit');
                if (submitBtn) submitBtn.addEventListener('click', () => predict());
                const clearBtn = $('#olapp-clear');
                if (clearBtn) clearBtn.addEventListener('click', clearInputs);
                if (ic) ic.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey && e.target.tagName !== 'TEXTAREA') { e.preventDefault(); predict(); } });
            } else if (config.mode === 'blocks') {
                const blocks = $('#olapp-blocks');
                if (blocks) { blocks.style.display = 'block'; renderLayout(config.layout || [], blocks); }
                for (const dep of (config.dependencies || [])) {
                    if (dep.trigger === 'click') {
                        for (const inputId of dep.inputs) {
                            const btn = $(`[data-id="${inputId}"]`);
                            if (btn && btn.tagName === 'BUTTON') {
                                btn.addEventListener('click', () => {
                                    const vals = dep.inputs.map(id => state.values[id] ?? null);
                                    api('POST', `/api/${dep.api_name}`, { data: vals })
                                        .then(r => { if (r.data) { const out = Array.isArray(r.data) ? r.data : [r.data]; dep.outputs.forEach((oid, i) => { const n = $(`[data-id="${oid}"]`); if (n && n.tagName === 'INPUT') { n.value = out[i] ?? ''; state.values[oid] = out[i]; } }); } })
                                        .catch(err => toast(err.message, 'error'));
                                });
                            }
                        }
                    }
                }
            }

            connectSSE();
        } catch (err) {
            const loading = $('#olapp-loading');
            if (loading) loading.innerHTML = `<div style="color:var(--olapp-error)">Failed to load: ${err.message}</div>`;
            toast('Failed to load application', 'error');
        }
    }

    document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', init) : init();
})();
