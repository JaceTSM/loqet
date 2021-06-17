# Deploy
Standard pip package deployment:
```shell
python setup.py sdist bdist_wheel upload
```

### Troubleshooting
If pypi doesn't like your readme, get more useful output with:
```shell
# pip install readme-renderer
readme_renderer README.md
```
