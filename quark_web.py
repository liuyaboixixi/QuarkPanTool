import asyncio
from flask import Flask, request, jsonify
from flasgger import Swagger
from quark import QuarkPanFileManager
from utils import custom_print

app = Flask(__name__)
swagger = Swagger(app)

# 初始化 quark_file_manager
quark_file_manager = QuarkPanFileManager(headless=False, slow_mo=500,
                                         folder_id='680e1caa6cc64b848665f316c4721f70',
                                         pdir_id='680e1caa6cc64b848665f316c4721f70')

# 获取目标目录ID
to_dir_id, to_dir_name = asyncio.run(quark_file_manager.load_folder_id())


@app.route('/save_files', methods=['POST'])
async def save_files():
    """
    保存夸克文件的接口
    ---
    parameters:
      - name: urls
        in: body
        type: object
        required: true
        properties:
          urls:
            type: array
            items:
              type: string
            description: 夸克文件分享链接列表
          folder_id:
            type: string
            description: 要保存的目录 ID
    responses:
      200:
        description: 保存成功
        schema:
          type: array
          items:
            type: object
            properties:
              url:
                type: string
                description: 分享链接
              status:
                type: string
                description: 状态（成功或错误）
              message:
                type: string
                description: 消息
      400:
        description: 请求参数错误
        schema:
          type: object
          properties:
            error:
              type: string
              description: 错误信息
    """
    # 获取请求参数
    data = request.json
    urls = data.get('urls', [])
    folder_id = data.get('folder_id', None)

    if not urls:
        return jsonify({'error': '分享地址为空！请先输入分享地址'}), 400

    custom_print(f"\r检测到分享链接中有{len(urls)}条，目标目录 ID: {folder_id}")
    responses = []

    for index, url in enumerate(urls):
        try:
            print(f"正在转存第{index + 1}个")
            result = await quark_file_manager.run(url.strip(), folder_id)  # 使用提供的目录 ID
            responses.append({'url': url, 'status': 'success', 'message': result})
        except Exception as e:
            responses.append({'url': url, 'status': 'error', 'message': str(e)})

    return jsonify(responses), 200


@app.route('/share_file', methods=['POST'])
async def share_file():
    """
    分享夸克文件的接口
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            share_option:
              type: string
              description: 分享选项(1分享, 2重试分享)
            url:
              type: string
              description: 需要分享的文件夹网页端页面地址（仅在 share_option 为 1 时必填）
            expired_type:
              type: integer
              description: 分享时长选项（1 1天, 2 7天, 3 30天, 4 永久）
            is_private:
              type: integer
              description: 是否加密（1 否, 2 是）
            passcode:
              type: string
              description: 分享提取码（可选）
          example:
            share_option: "1"
            url: "https://pan.quark.cn/list#/list/all/3b99735be39346b8916458e2fa510390-%E8%87%AA%E5%8A%A8%E5%AE%9A%E6%97%B6%E5%88%86%E4%BA%AB/4ff3127fd891421e9597ab556f432175-X%20%E5%B0%8F.%E5%B7%B7%E4%BA%BAJ%E5%AE%B6%202024"
            expired_type: 4
            is_private: "1"
            passcode: ""
    responses:
      200:
        description: 分享成功
        schema:
          type: object
          properties:
            share_links:
              type: array
              items:
                type: string
      400:
        description: 请求参数错误
        schema:
          type: object
          properties:
            error:
              type: string
              description: 错误信息
    """

    data = request.json
    share_option = data.get('share_option')

    # 验证分享选项
    if share_option not in ['1', '2']:
        return jsonify({'error': '无效的分享选项！'}), 400

    url = data.get('url')
    if share_option == '1' and (not url or len(url.strip()) < 20):
        return jsonify({'error': '无效的分享链接！'}), 400

    # 读取重试链接
    expired_option = {"1": 2, "2": 3, "3": 4, "4": 1}
    select_option = str(data.get('expired_type', 4))  # 默认为 4
    _expired_type = expired_option.get(select_option, 4)

    is_private = data.get('is_private', '1')  # 默认为不加密
    url_encrypt = 2 if is_private == '2' else 1
    passcode = data.get('passcode', '') if url_encrypt == 2 else ''

    try:
        share_links = await quark_file_manager.http_share_run(
            url.strip(), folder_id=to_dir_id, url_type=int(url_encrypt),
            expired_type=int(_expired_type), password=passcode)

        return jsonify({'share_links': share_links}), 200  # 返回分享链接
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
