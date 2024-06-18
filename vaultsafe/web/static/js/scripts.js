function copyToClipboard(elementId) {
  var copyText = document.getElementById(elementId);
  copyText.type = 'text';  // Change the input type to text
  copyText.select();
  document.execCommand('copy');
  copyText.type = 'password';  // Change the input type back to password
  alert('Copied to clipboard: ' + copyText.value);
}