import numpy
portal_guid_list = [
"d7ef946e2a874f9cb6c95b6121d20a4b.16","01cf9462bb224b6997cd11d8fd99b4ab.16","e9f89a6608a646aab112cfd3cb63cd17.16","7d445f84239d48a786eaf7a6b0868232.16","8c439807c2fc41b3a7e89df60b6617c7.16","9b262cc432a24ab3aaf076c0e20d4014.16","c0a27a1badee4fdc94bd1180776e945d.16","6729c68ebaee40c78af4c1481ec46016.16","499dee356bab4b9dba1dfa6ae2fc6979.16","b61f808294844cf1b70d39989b263b32.16","d69a9ae6733e4c9487808cde64564be9.16","5b355df9569d42bda75a24bb53faae64.16","c6ac5bd1f7344d9fb02ae0ea180dcb4e.16","3c76246d83034a2f93d7e0dae956e451.16","99f2cf56f74b4f64abaa04ea55b0503b.16","c20365d801534dbc8ca53734d79e85a4.16","ee11c1511d004f4ebcee1c5e314079f3.16","ca09681350fb46509c59a8b7268a5ab3.16","42d026ec3e6747f08f489a1d90623c71.16",
]
numpy.save('guid_list.npy', portal_guid_list)
# portal_guid_list2 = numpy.load('guid_list.npy').tolist()
# print portal_guid_list2
# portal_guid_list2.append('123')
# print portal_guid_list2[-1]