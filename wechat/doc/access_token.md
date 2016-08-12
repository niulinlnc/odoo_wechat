## 公众平台的api调用所需的`access_token`的使用及生成方式说明

- 为了保密`appsecrect`，第三方需要一个`access_token`获取和刷新的中控服务器。而其他业务逻辑服务器所使用的`access_token`均来自于该中控服务器，不应该各自去刷新，否则会造成`access_token`覆盖而影响业务；
- 目前`access_token`的有效期通过返回的`expire_in`来传达，目前是7200秒之内的值。中控服务器需要根据这个有效时间提前去刷新新`access_token`。在刷新过程中，中控服务器对外输出的依然是老`access_token`，此时公众平台后台会保证在刷新短时间内，新老`access_token`都可用，这保证了第三方业务的平滑过渡；
- `access_token`的有效时间可能会在未来有调整，所以中控服务器不仅需要内部定时主动刷新，还需要提供被动刷新`access_token`的接口，这样便于业务服务器在API调用获知`access_token`已超时的情况下，可以触发`access_token`的刷新流程。
