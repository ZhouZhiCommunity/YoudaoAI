import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from tools.ai_rewriting import rewrite_paper_paragraph
from tools.pdf_util import get_segment_from_pdf
import tempfile
from docx import Document
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB最大上传
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'md'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/rewrite', methods=['POST'])
def rewrite_text():
    """
    文本改写接口
    接收JSON: {"text": "需要改写的文本"}
    返回JSON: {"success": true, "rewritten_text": "改写后的文本"}
    """
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': '请提供需要改写的文本'
            }), 400
        original_text = data.get('text', '').strip()
        if not original_text:
            return jsonify({
                'success': False,
                'error': '文本内容不能为空'
            }), 400
        # 调用AI改写函数
        rewritten_text = rewrite_paper_paragraph(
            paragraph=original_text,
            temperature=data.get('temperature', 0.5),
            use_knowledge_base=data.get('use_knowledge_base', True)
        )
        return jsonify({
            'success': True,
            'original_text': original_text,
            'rewritten_text': rewritten_text,
            'original_length': len(original_text),
            'rewritten_length': len(rewritten_text)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'改写失败: {str(e)}'
        }), 500


@app.route('/api/rewrite-file', methods=['POST'])
def rewrite_file():
    """
    文件改写接口
    接收文件: PDF/DOCX/TXT/MD
    返回JSON: {"success": true, "segments": [{"original": "...", "rewritten": "..."}]}
    """
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '未找到上传的文件'
            }), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '未选择文件'
            }), 400
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'不支持的文件格式，仅支持: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        filename = file.filename
        file_ext = filename.rsplit('.', 1)[1].lower()
        # 获取可选参数
        temperature = float(request.form.get('temperature', 0.5))
        use_knowledge_base = request.form.get('use_knowledge_base', 'true').lower() == 'true'
        # 创建临时文件保存上传的文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as tmp_file:
            file.save(tmp_file.name)
            tmp_file_path = tmp_file.name
        try:
            segments = []
            if file_ext == 'pdf':
                pdf_segments = get_segment_from_pdf(tmp_file_path)
                # 加线程池，试了下，2个以上并发就报（您当前使用该API的并发数过高，请降低并发，或联系客服增加限额。）
                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = []
                    for segment in pdf_segments:
                        original_text = segment['text']
                        future = executor.submit(
                            rewrite_paper_paragraph,
                            paragraph=original_text,
                            temperature=temperature,
                            use_knowledge_base=use_knowledge_base
                        )
                        futures.append(future)
                    # 合并按顺序取
                    for idx, (segment, future) in enumerate(zip(pdf_segments, futures)):
                        try:
                            rewritten_text = future.result()
                        except Exception as e:
                            rewritten_text = f"[改写失败: {str(e)}]"
                        segments.append({
                            'index': idx + 1,
                            'page': segment.get('page'),
                            'original': segment['text'],
                            'rewritten': rewritten_text,
                            'original_length': len(segment['text']),
                            'rewritten_length': len(rewritten_text)
                        })

            elif file_ext in ['txt', 'md']:
                # 处理文本文件
                with open(tmp_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # 按段落分割（空行分割）
                paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                for idx, paragraph in enumerate(paragraphs):
                    rewritten_text = rewrite_paper_paragraph(
                        paragraph=paragraph,
                        temperature=temperature,
                        use_knowledge_base=use_knowledge_base
                    )
                    segments.append({
                        'index': idx + 1,
                        'original': paragraph,
                        'rewritten': rewritten_text,
                        'original_length': len(paragraph),
                        'rewritten_length': len(rewritten_text)
                    })
            elif file_ext == 'docx':
                # 处理DOCX文件
                try:
                    doc = Document(tmp_file_path)
                    for idx, para in enumerate(doc.paragraphs):
                        if para.text.strip():
                            original_text = para.text.strip()
                            rewritten_text = rewrite_paper_paragraph(
                                paragraph=original_text,
                                temperature=temperature,
                                use_knowledge_base=use_knowledge_base
                            )
                            segments.append({
                                'index': idx + 1,
                                'original': original_text,
                                'rewritten': rewritten_text,
                                'original_length': len(original_text),
                                'rewritten_length': len(rewritten_text)
                            })
                except ImportError:
                    return jsonify({
                        'success': False,
                        'error': 'DOCX处理需要安装python-docx库'
                    }), 500
            # 计算统计信息
            total_original_length = sum(s['original_length'] for s in segments)
            total_rewritten_length = sum(s['rewritten_length'] for s in segments)
            return jsonify({
                'success': True,
                'filename': filename,
                'file_type': file_ext,
                'segments': segments,
                'total_segments': len(segments),
                'statistics': {
                    'total_original_length': total_original_length,
                    'total_rewritten_length': total_rewritten_length,
                    'length_change': total_rewritten_length - total_original_length
                }
            })
        finally:
            # 清理临时文件
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'文件处理失败: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'service': '有道降AI - 论文改写服务',
        'version': '1.0.0'
    })


@app.route('/', methods=['GET'])
def index():
    """根路径"""
    return jsonify({
        'message': '有道降AI API服务',
        'endpoints': {
            'POST /api/rewrite': '文本改写接口',
            'POST /api/rewrite-file': '文件改写接口',
            'GET /api/health': '健康检查'
        }
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
