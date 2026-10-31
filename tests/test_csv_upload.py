import io

from app import create_app


def test_valid_csv_upload():
    app = create_app()
    client = app.test_client()
    csv_payload = """duration,protocol_type,service,flag,src_bytes,dst_bytes,land,wrong_fragment,urgent,hot,num_failed_logins,logged_in,num_compromised,root_shell,su_attempted,num_root,num_file_creations,num_shells,num_access_files,num_outbound_cmds,is_host_login,is_guest_login,count,srv_count,serror_rate,srv_serror_rate,rerror_rate,srv_rerror_rate,same_srv_rate,diff_srv_rate,srv_diff_host_rate,dst_host_count,dst_host_srv_count,dst_host_same_srv_rate,dst_host_diff_srv_rate,dst_host_same_src_port_rate,dst_host_srv_diff_host_rate,dst_host_serror_rate,dst_host_srv_serror_rate,dst_host_rerror_rate,dst_host_srv_rerror_rate
0,tcp,http,SF,10,20,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,1,0.0,0.0,0.0,0.0,1.0,0.0,0.0,100,100,1.0,0.0,0.1,0.0,0.0,0.0,0.0,0.0
1,tcp,ftp,SF,20,30,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,2,2,0.1,0.1,0.0,0.0,0.9,0.1,0.0,90,90,0.9,0.1,0.2,0.1,0.1,0.1,0.1,0.1
"""
    response = client.post('/analyze', data={'csv_file': (io.BytesIO(csv_payload.encode('utf-8')), 'sample.csv')}, content_type='multipart/form-data')
    assert response.status_code == 200


def test_invalid_csv_upload():
    app = create_app()
    client = app.test_client()
    response = client.post('/analyze', data={'csv_file': (io.BytesIO(b'not,a,valid,csv'), 'bad.csv')}, content_type='multipart/form-data')
    assert response.status_code == 200


def test_missing_csv_columns():
    app = create_app()
    client = app.test_client()
    csv_payload = "duration,protocol_type\n0,tcp\n"
    response = client.post('/analyze', data={'csv_file': (io.BytesIO(csv_payload.encode('utf-8')), 'missing.csv')}, content_type='multipart/form-data')
    assert response.status_code == 200


def test_empty_csv():
    app = create_app()
    client = app.test_client()
    response = client.post('/analyze', data={'csv_file': (io.BytesIO(b''), 'empty.csv')}, content_type='multipart/form-data')
    assert response.status_code == 200


def test_csv_more_than_100_rows():
    app = create_app()
    client = app.test_client()
    rows = ["duration,protocol_type,service,flag,src_bytes,dst_bytes,land,wrong_fragment,urgent,hot,num_failed_logins,logged_in,num_compromised,root_shell,su_attempted,num_root,num_file_creations,num_shells,num_access_files,num_outbound_cmds,is_host_login,is_guest_login,count,srv_count,serror_rate,srv_serror_rate,rerror_rate,srv_rerror_rate,same_srv_rate,diff_srv_rate,srv_diff_host_rate,dst_host_count,dst_host_srv_count,dst_host_same_srv_rate,dst_host_diff_srv_rate,dst_host_same_src_port_rate,dst_host_srv_diff_host_rate,dst_host_serror_rate,dst_host_srv_serror_rate,dst_host_rerror_rate,dst_host_srv_rerror_rate"]
    for i in range(101):
        rows.append(f"{i},tcp,http,SF,10,20,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,1,0.0,0.0,0.0,0.0,1.0,0.0,0.0,100,100,1.0,0.0,0.1,0.0,0.0,0.0,0.0,0.0")
    response = client.post('/analyze', data={'csv_file': (io.BytesIO("\n".join(rows).encode('utf-8')), 'too_many.csv')}, content_type='multipart/form-data')
    assert response.status_code == 200


def test_invalid_numeric_csv_values():
    app = create_app()
    client = app.test_client()
    csv_payload = "duration,protocol_type,service,flag,src_bytes,dst_bytes,land,wrong_fragment,urgent,hot,num_failed_logins,logged_in,num_compromised,root_shell,su_attempted,num_root,num_file_creations,num_shells,num_access_files,num_outbound_cmds,is_host_login,is_guest_login,count,srv_count,serror_rate,srv_serror_rate,rerror_rate,srv_rerror_rate,same_srv_rate,diff_srv_rate,srv_diff_host_rate,dst_host_count,dst_host_srv_count,dst_host_same_srv_rate,dst_host_diff_srv_rate,dst_host_same_src_port_rate,dst_host_srv_diff_host_rate,dst_host_serror_rate,dst_host_srv_serror_rate,dst_host_rerror_rate,dst_host_srv_rerror_rate\ninvalid,tcp,http,SF,10,20,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,1,0.0,0.0,0.0,0.0,1.0,0.0,0.0,100,100,1.0,0.0,0.1,0.0,0.0,0.0,0.0,0.0"
    response = client.post('/analyze', data={'csv_file': (io.BytesIO(csv_payload.encode('utf-8')), 'invalid_numeric.csv')}, content_type='multipart/form-data')
    assert response.status_code == 200
