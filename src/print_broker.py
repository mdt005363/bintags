"""Send jobs to printers. The phone never talks to a printer directly — this runs on
the Flask host (Windows box with the shared Zebra + laser printer)."""
import socket


def send_zpl(zpl, cfg):
    """Prefer RAW spool to the shared Windows queue; fall back to raw TCP :9100."""
    t = cfg["thermal"]
    share = t.get("printer_share")
    ip = t.get("printer_ip")
    data = zpl.encode("utf-8")
    if share:
        try:
            return _spool_raw_windows(share, data, "HIO bin tag")
        except Exception as e:  # noqa: BLE001 - fall back to network path
            if not ip:
                raise
            print(f"RAW spool failed ({e}); trying TCP {ip}:{t.get('printer_port',9100)}")
    if ip:
        return _send_tcp(ip, int(t.get("printer_port", 9100)), data)
    raise RuntimeError("No thermal printer_share or printer_ip configured.")


def print_pdf(pdf_bytes, cfg, printer_name=None):
    """Print a rendered PDF to the laser printer (Windows). Returns a status string."""
    import os
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".pdf")
    with os.fdopen(fd, "wb") as f:
        f.write(pdf_bytes)
    try:
        import win32api  # type: ignore
        win32api.ShellExecute(0, "print", path, None, ".", 0)
        return f"sent {path} to default PDF print handler"
    except ImportError:
        return f"pywin32 not available; PDF saved at {path} (open and print manually)"


def _spool_raw_windows(share, data, doc_name):
    import win32print  # type: ignore
    h = win32print.OpenPrinter(share)
    try:
        job = win32print.StartDocPrinter(h, 1, (doc_name, None, "RAW"))
        win32print.StartPagePrinter(h)
        win32print.WritePrinter(h, data)
        win32print.EndPagePrinter(h)
        win32print.EndDocPrinter(h)
        return f"spooled RAW job {job} to {share}"
    finally:
        win32print.ClosePrinter(h)


def _send_tcp(ip, port, data):
    with socket.create_connection((ip, port), timeout=10) as s:
        s.sendall(data)
    return f"sent {len(data)} bytes to {ip}:{port}"
